from aiohttp import web
from aiohttp_index import IndexMiddleware
import logging
import socketio

from rpi_cam.tools import get_logger, CLIENT_BUILD_DIR, CAM_DATA_DIR
from rpi_cam.capture import get_frame_manager, Drivers
from rpi_cam.capture.frame_manager import ImageError


logger = get_logger('rpi_cam.server')

sio = socketio.AsyncServer()
app = web.Application(middlewares=[IndexMiddleware()])
sio.attach(app)


async def close_all_connections():
    for sock in sio.eio.sockets.values():
        await sock.close()


async def send_camera_settings(sid=None):
    camera_setings = {
        'frameRate': app['frame_rate'],
        'autoShoot': int(app['auto_shoot']),
        'shootTimeout': app['shoot_timeout'],
        'idleWhenAlone': int(app['idle_when_alone']),
    }

    logger.info('Update user(s) with camera settings.')
    await sio.emit('settings',
                   camera_setings,
                   sid=sid,
                   namespace='/cam')


async def send_log_message(msg, title=None, sid=None, is_error=False):
    logger.info('Sending log message to client {sid} (None for all) about "{title}" (is error={is_error}).'.format(
        sid=sid, title=title, is_error=is_error,
    ))

    msg_type = 'info'

    if is_error:
        msg_type = 'error'

    await sio.emit('log',
                   {
                       'type': msg_type,
                       'title': title,
                       'text': repr(msg),
                   },
                   room=sid, namespace='/cam')


async def report_error(msg, title=None, sid=None):
    await send_log_message(msg, title=title, sid=sid, is_error=True)


async def send_latest_images_update(sid=None):
    try:
        await sio.emit('latest images',
                       [img.__dict__ for img in app['frame_manager'].get_latest_images()],
                       sid=sid,
                       namespace='/cam')
    except ImageError as e:
        await report_error(e, 'send_latest_images_update', sid=sid)


@sio.on('connect', namespace='/cam')
async def connect(sid, environ):
    logger.warning('Connection established: {sid} from {origin}.'.format(
        sid=sid, origin=environ.get('HTTP_ORIGIN', 'unknown origin')
    ))

    if not app['frame_manager'].is_started:
        logger.warning('Starting camera...')
        app['frame_manager'].start()

    app['client'] += 1

    await send_camera_settings(sid)

    logger.info('Initialising user with latest images.')
    await send_latest_images_update(sid)

    await send_log_message('Welcome to RPi camera', 'Connect')


@sio.on('update settings', namespace='/cam')
async def message(sid, data):
    logger.warning('Updating camera settings to {settings}'.format(settings=data))

    try:
        app['frame_rate'] = int(data['frameRate'])
        app['auto_shoot'] = bool(data['autoShoot'])
        app['shoot_timeout'] = int(data['shootTimeout'])
        app['idle_when_alone'] = bool(data['idleWhenAlone'])
    except ValueError:
        logger.error('Error updating camera settings to {settings}'.format(settings=data))

    await send_camera_settings(sid)


async def shoot(sid=None):
    if not app['frame_manager'].is_started:
        logger.error('Trying to shoot from idle frame manager.')
        return

    try:
        img = app['frame_manager'].shoot()

        if sid is not None and img is not None:
            logger.debug('Sending update for recently shot image of {filename}'.format(filename=img.filename))
            await sio.emit('image', img.__dict__, room=sid, namespace='/cam')

        logger.debug('Sending latest images update.')
        await send_latest_images_update()

        await send_log_message('Successfully shot image: {filename}'.format(filename=img.filename),
                               'Shoot image', sid=sid)
    except ImageError as e:
        await report_error(e, 'shoot', sid=sid)


@sio.on('shoot', namespace='/cam')
async def message(sid):
    await shoot(sid)


@sio.on('disconnect', namespace='/cam')
def disconnect(sid):
    logger.warning('Disconnected: %s' % sid)

    app['client'] -= 1

    if app['client'] < 1 and app['frame_manager'].is_started:
        logger.warning('No more clients.')
        if app['idle_when_alone']:
            logger.warning('Closing camera...')
            app['frame_manager'].stop()


async def stream_thumbs():
    """Send new image notification to client."""
    logger.debug('Starting thumbnail streaming background task.')
    while True:
        await sio.sleep(1 / app['frame_rate'])

        if app['frame_manager'].is_started:
            preview = app['frame_manager'].preview()

            logger.debug('Sending frame update for {filename} preview'.format(filename=preview.filename))
            await sio.emit('preview', preview.__dict__, namespace='/cam')


async def auto_shoot():
    """Perform periodic shoots."""
    logger.debug('Starting auto shoot background task.')
    while True:
        await sio.sleep(app['shoot_timeout'])

        if app['frame_manager'].is_started and app['auto_shoot']:
            await shoot()


async def send_fps_updates():
    """Perform periodic fps updates."""
    logger.debug('Starting FPS update background task.')
    while True:
        await sio.sleep(1)

        if app['frame_manager'].is_started:
            logger.debug('FPS: %s' % app['frame_manager'].fps_counter.fps)
            await sio.emit('fps', {'fps': app['frame_manager'].fps_counter.fps}, namespace='/cam')


def run(driver=Drivers.RPI, frame_rate=24,
        cam_data_dir=CAM_DATA_DIR, client_build_dir=CLIENT_BUILD_DIR,
        log_level=logging.INFO,
        **kwargs):
    logger.setLevel(log_level)

    app['frame_rate'] = frame_rate
    app['auto_shoot'] = False
    app['shoot_timeout'] = 5
    app['client'] = 0
    app['idle_when_alone'] = True

    app['frame_manager'] = get_frame_manager(driver, cam_data_dir,
                                             url_prefix='/cam_data',
                                             logger=get_logger('rpi_cam.capture.frame_manager', level=log_level),
                                             )

    app.router.add_static('/cam_data', cam_data_dir, show_index=True)
    app.router.add_static('/', client_build_dir)

    logger.warning('Starting background tasks.')
    sio.start_background_task(stream_thumbs)
    sio.start_background_task(auto_shoot)
    sio.start_background_task(send_fps_updates)

    logger.warning('Starting server with parameter set: {kwargs}.'.format(kwargs=kwargs))
    web.run_app(app, **kwargs)

    if app['frame_manager'].is_started:
        app['frame_manager'].stop()


if __name__ == '__main__':
    run()
