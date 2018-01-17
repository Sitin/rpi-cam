from aiohttp import web
from aiohttp_index import IndexMiddleware
import logging
import socketio

from rpi_cam.tools import get_logger, CLIENT_BUILD_DIR, CAM_DATA_DIR
from rpi_cam.capture import get_frame_manager, Drivers
from rpi_cam.capture.frame_manager import ImageError, DEFAULT_PREVIEW_RESOLUTION
from rpi_cam.capture.rpi_capture.picamera_options import DEFAULT_PREVIEW_SENSOR_MODE


class RPiCameraServer(object):
    def __init__(self, driver=Drivers.RPI, frame_rate=24,
                 cam_data_dir=CAM_DATA_DIR, client_build_dir=CLIENT_BUILD_DIR,
                 log_level=logging.INFO,
                 shoot_at_startup=False,
                 preview_sensor_mode=DEFAULT_PREVIEW_SENSOR_MODE,
                 preview_resolution=DEFAULT_PREVIEW_RESOLUTION,
                 **web_app_args):
        self.sio = socketio.AsyncServer()
        self.logger = get_logger('rpi_cam.server', level=log_level, sio=self.sio, namespace='/cam')

        self.app = web.Application(middlewares=[IndexMiddleware()])
        self.sio.attach(self.app)

        self.frame_rate = frame_rate
        self.default_auto_shoot = False
        self.auto_shoot = False
        self.shoot_timeout = 5
        self.clients = 0
        self.idle_when_alone = True
        self.report_timeout = 30
        self.camera_idle_timeout = 5
        self.camera_stop_task = None
        self.shoot_at_startup = shoot_at_startup
        self.startup_shooting_timeout = 300
        self.latest_preview = None

        self.frame_manager = get_frame_manager(
            driver, cam_data_dir,
            url_prefix='/cam_data',
            logger=get_logger('rpi_cam.capture.frame_manager', level=log_level,
                              sio=self.sio, namespace='/cam'),
            preview_sensor_mode=preview_sensor_mode,
            preview_resolution=preview_resolution,
        )

        self.web_app_args = web_app_args

        self.app.router.add_static('/cam_data', cam_data_dir, show_index=True)
        self.app.router.add_get('/latest', self.get_latest_preview)
        self.app.router.add_static('/', client_build_dir)

        self.logger.warning('Starting background tasks.')
        self.sio.start_background_task(self.stream_thumbs)
        self.sio.start_background_task(self.auto_shoot_task)
        self.sio.start_background_task(self.send_fps_updates)
        self.sio.start_background_task(self.send_status_reports)
        self.startup_shooting_task = self.sio.start_background_task(self.startup_shooting)

        self._define_events()

    def run(self):
        self.logger.warning('Starting server with parameter set: {kwargs}.'.format(kwargs=self.web_app_args))
        web.run_app(self.app, **self.web_app_args)

        if self.frame_manager.is_started:
            self.frame_manager.stop()

    def _define_events(self):
        @self.sio.on('update settings', namespace='/cam')
        async def message(sid, data):
            self.logger.warning('Updating camera settings to {settings}'.format(settings=data))

            try:
                self.frame_rate = int(data['frameRate'])
                self.auto_shoot = bool(data['autoShoot'])
                self.shoot_timeout = int(data['shootTimeout'])
                self.idle_when_alone = bool(data['idleWhenAlone'])
                self.report_timeout = int(data['reportTimeout'])
                self.camera_idle_timeout = int(data['cameraIdleTimeout'])
            except ValueError:
                self.logger.error('Error updating camera settings to {settings}'.format(settings=data))

            await self.send_camera_settings(sid)

        @self.sio.on('shoot', namespace='/cam')
        async def message(sid):
            await self.shoot(sid)

        @self.sio.on('connect', namespace='/cam')
        async def connect(sid, environ):
            self.logger.warning('Connection established: {sid} from {origin}.'.format(
                sid=sid, origin=environ.get('HTTP_ORIGIN', 'unknown origin')
            ))

            if not self.frame_manager.is_started:
                self.logger.warning('Starting camera...')
                self.frame_manager.start()

            self.clients += 1

            if self.camera_stop_task is not None:
                self.logger.info('Cancelling postponed camera stop.')
                self.camera_stop_task.cancel()
                self.camera_stop_task = None

            if self.startup_shooting_task is not None:
                self.logger.info('Cancelling startup time lapse.')
                self.startup_shooting_task.cancel()
                self.startup_shooting_task = None
                self.auto_shoot = self.default_auto_shoot

            await self.send_camera_settings(sid)

            self.logger.info('Initialising user with latest images.')
            await self.send_latest_images_update(sid)

            await self.send_status_report()

        @self.sio.on('disconnect', namespace='/cam')
        def disconnect(sid):
            self.logger.warning('Disconnected: %s' % sid)

            self.clients -= 1

            if self.clients < 1 and self.frame_manager.is_started:
                self.logger.warning('No more clients.')
                if self.idle_when_alone:
                    self.stop_camera()

    async def get_latest_preview(self, request):
        if self.latest_preview is None:
            await self.make_preview()

        return web.json_response(self.latest_preview.__dict__)

    def stop_camera(self):
        if self.camera_idle_timeout > 0:
            self.logger.warning('Closing camera...')
            self.camera_stop_task = self.sio.start_background_task(self.postponed_camera_stop)
        else:
            self.logger.warning('Stop camera immediately...')
            self.frame_manager.stop()

    async def close_all_connections(self):
        for sock in self.sio.eio.sockets.values():
            await sock.close()
    
    async def send_camera_settings(self, sid=None):
        camera_setings = {
            'frameRate': self.frame_rate,
            'autoShoot': int(self.auto_shoot),
            'shootTimeout': self.shoot_timeout,
            'idleWhenAlone': int(self.idle_when_alone),
            'reportTimeout': int(self.report_timeout),
            'cameraIdleTimeout': int(self.camera_idle_timeout),
        }

        self.logger.info('Update user(s) with camera settings.')
        await self.sio.emit('settings',
                            camera_setings,
                            sid=sid,
                            namespace='/cam')
    
    async def send_latest_images_update(self, sid=None):
        try:
            await self.sio.emit('latest images',
                                [img.__dict__ for img in self.frame_manager.get_latest_images()],
                                sid=sid,
                                namespace='/cam')
        except ImageError as e:
            await self.logger.error(e)
    
    async def send_status_report(self):
        report = self.frame_manager.report_state()

        # We do not send empty reports
        if len(report) < 1:
            return

        if report['is_critical']:
            self.logger.error(report['data'])
        else:
            self.logger.info(report['data'])

    async def shoot(self, sid=None):
        if not self.frame_manager.is_started:
            self.logger.error('Trying to shoot from idle frame manager.')
            return

        try:
            img = self.frame_manager.shoot()

            if sid is not None and img is not None:
                self.logger.debug('Sending update for recently shot image of {filename}'.format(filename=img.filename))
                await self.sio.emit('image', img.__dict__, room=sid, namespace='/cam')

            self.logger.debug('Sending latest images update.')
            await self.send_latest_images_update()

            self.logger.info('Successfully shot image: {filename}'.format(filename=img.filename))

        except ImageError as e:
            await self.logger.error(e)

    def should_make_preview(self):
        """Determines whether preview should be taken and transferred to clients."""
        return self.frame_manager.is_started and self.clients > 0

    async def make_preview(self):
        preview = self.frame_manager.preview()
        self.latest_preview = preview

        self.logger.debug('Sending frame update for {filename} preview'.format(filename=preview.filename))
        await self.sio.emit('preview', preview.__dict__, namespace='/cam')

    async def stream_thumbs(self):
        """Send new image notification to client."""
        self.logger.debug('Starting thumbnail streaming background task.')
        while True:
            await self.sio.sleep(1 / self.frame_rate)

            if self.should_make_preview():
                await self.make_preview()
    
    async def auto_shoot_task(self):
        """Perform periodic shoots."""
        self.logger.debug('Starting auto shoot background task.')
        while True:
            if self.frame_manager.is_started and self.auto_shoot:
                await self.shoot()

            await self.sio.sleep(self.shoot_timeout)

    async def send_fps_updates(self):
        """Perform periodic fps updates."""
        self.logger.debug('Starting FPS update background task.')
        while True:
            await self.sio.sleep(1)
    
            if self.frame_manager.is_started:
                self.logger.debug('FPS: %s' % self.frame_manager.fps_counter.fps)
                await self.sio.emit('fps', {'fps': self.frame_manager.fps_counter.fps}, namespace='/cam')
    
    async def send_status_reports(self):
        """Sends periodic status reports to client."""
        self.logger.debug('Starting camera reporting background task.')
        while True:
            await self.send_status_report()
            await self.sio.sleep(self.report_timeout)
    
    async def postponed_camera_stop(self):
        """Stops the camera after a certain time."""
        self.logger.info('Entering postponed camera stop background task.')
    
        time_to_stop = self.camera_idle_timeout
    
        while self.frame_manager.is_started:
            self.logger.info('Camera will stop after after {time_to_stop} seconds.'.format(time_to_stop=time_to_stop))
    
            if time_to_stop <= 0:
                self.frame_manager.stop()

                self.logger.info('Camera stopped after {timeout} timeout.'.format(
                    timeout=self.camera_idle_timeout
                ))
    
            time_to_stop -= 1
            await self.sio.sleep(1)

    async def startup_shooting(self):
        """Shoots certain time at the startup and then turn camera off."""
        if not self.shoot_at_startup:
            return

        shooting_timeout = max([self.startup_shooting_timeout - self.camera_idle_timeout, 0])

        self.logger.info('Info starting startup time lapse for {seconds} seconds.'.format(seconds=shooting_timeout))
        self.auto_shoot = True
        self.frame_manager.start()

        await self.sio.sleep(shooting_timeout)

        self.logger.info('Stopping startup time lapse...')
        self.auto_shoot = self.default_auto_shoot
        self.stop_camera()


def run(**kwargs):
    server = RPiCameraServer(**kwargs)
    server.run()


if __name__ == '__main__':
    run()
