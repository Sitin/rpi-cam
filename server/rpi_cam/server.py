from aiohttp import web
from aiohttp_index import IndexMiddleware
import socketio

from rpi_cam.tools import get_logger, CLIENT_BUILD_DIR
from rpi_cam.capture import get_frame_manager, Drivers


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
    }

    logger.info('Update user(s) with camera settings.')
    await sio.emit('settings',
                   camera_setings,
                   sid=sid,
                   namespace='/cam')


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
    await sio.emit('latest images',
                   [img.__dict__ for img in app['frame_manager'].get_latest_images()],
                   sid=sid,
                   namespace='/cam')


@sio.on('update settings', namespace='/cam')
async def message(sid, data):
    logger.warning('Updating camera settings to {settings}'.format(settings=data))

    try:
        app['frame_rate'] = int(data['frameRate'])
        app['auto_shoot'] = bool(data['autoShoot'])
        app['shoot_timeout'] = int(data['shootTimeout'])
    except ValueError:
        logger.error('Error updating camera settings to {settings}'.format(settings=data))

    await send_camera_settings(sid)


async def shoot(sid=None):
    img = app['frame_manager'].shoot()

    if sid is not None:
        logger.debug('Sending image update for {filename} thumb'.format(filename=img.filename))
        await sio.emit('image', img.__dict__, room=sid, namespace='/cam')

    logger.debug('Sending latest images update.')
    await sio.emit('latest images',
                   [img.__dict__ for img in app['frame_manager'].get_latest_images()],
                   namespace='/cam')


@sio.on('shoot', namespace='/cam')
async def message(sid):
    shoot(sid)


@sio.on('disconnect', namespace='/cam')
def disconnect(sid):
    logger.warning('Disconnected: %s' % sid)

    app['client'] -= 1

    if app['client'] < 1 and app['frame_manager'].is_started:
        logger.warning('No more clients. Closing camera...')
        app['frame_manager'].stop()


async def stream_thumbs():
    """Send new image notification to client."""
    app['frame_count'] = 0

    while True:
        await sio.sleep(1 / app['frame_rate'])

        if app['frame_manager'].is_started:
            app['frame_count'] += 1
            preview = app['frame_manager'].preview()

            logger.debug('Sending frame update for {filename} preview'.format(filename=preview.filename))
            await sio.emit('preview', preview.__dict__, namespace='/cam')


async def auto_shoot():
    """Perform periodic shoots."""
    while True:
        await sio.sleep(app['shoot_timeout'])

        if app['frame_manager'].is_started and app['auto_shoot']:
            await shoot()


def run(driver=Drivers.RPI, frame_rate=24, **kwargs):
    app['frame_rate'] = frame_rate
    app['auto_shoot'] = False
    app['shoot_timeout'] = 5
    app['client'] = 0

    app['frame_manager'] = get_frame_manager(driver, url_prefix='/cam_data')

    app.router.add_static('/cam_data', app['frame_manager'].path, show_index=True)
    app.router.add_static('/', CLIENT_BUILD_DIR)

    logger.warning('Starting background tasks.')
    sio.start_background_task(stream_thumbs)
    sio.start_background_task(auto_shoot)

    logger.warning('Starting server.')
    web.run_app(app, **kwargs)

    if app['frame_manager'].is_started:
        app['frame_manager'].stop()


if __name__ == '__main__':
    run()
