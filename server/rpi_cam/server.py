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


@sio.on('connect', namespace='/cam')
async def connect(sid, environ):
    logger.warning('Connection established: {sid} from {origin}.'.format(
        sid=sid, origin=environ.get('HTTP_ORIGIN', 'unknown origin')
    ))

    if not app['frame_manager'].is_started:
        logger.warning('Starting camera...')
        app['frame_manager'].start()

    app['client'] += 1

    logger.info('Initialising user with latest images.')
    await sio.emit('latest images',
                   [img.__dict__ for img in app['frame_manager'].get_latest_images()],
                   namespace='/cam')


@sio.on('shoot', namespace='/cam')
async def message(sid):
    img = app['frame_manager'].shoot()

    logger.debug('Sending image update for {filename} thumb'.format(filename=img.filename))
    await sio.emit('image', img.__dict__, room=sid, namespace='/cam')

    logger.debug('Sending latest images update.')
    await sio.emit('latest images',
                   [img.__dict__ for img in app['frame_manager'].get_latest_images()],
                   namespace='/cam')


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
    manager = app['frame_manager']

    while True:
        await sio.sleep(1 / app['frame_rate'])

        if manager.is_started:
            app['frame_count'] += 1
            preview = manager.preview()

            logger.debug('Sending frame update for {filename} preview'.format(filename=preview.filename))
            await sio.emit('preview', preview.__dict__, namespace='/cam')


def run(driver=Drivers.RPI, frame_rate=24, **kwargs):
    app['frame_rate'] = frame_rate
    app['client'] = 0

    app['frame_manager'] = get_frame_manager(driver, url_prefix='/cam_data')

    app.router.add_static('/cam_data', app['frame_manager'].path, show_index=True)
    app.router.add_static('/', CLIENT_BUILD_DIR)

    logger.warning('Starting background tasks.')
    sio.start_background_task(stream_thumbs)
    logger.warning('Starting server.')
    web.run_app(app, **kwargs)

    if app['frame_manager'].is_started:
        app['frame_manager'].stop()


if __name__ == '__main__':
    run()
