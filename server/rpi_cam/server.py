import os

from aiohttp import web
import socketio

from rpi_cam.tools import get_logger, CLIENT_BUILD_DIR
from rpi_cam.capture import get_frame_manager, Drivers


logger = get_logger('rpi_cam.server')

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)


def set_img_path(img):
    img.set_path('/cam_data')
    return img


def set_thumb_path(thumb):
    thumb.set_path('/cam_data/thumbs')
    return thumb


async def close_all_connections():
    for sock in sio.eio.sockets.values():
        await sock.close()


async def index(request):
    """Serve the client-side application."""
    with open(os.path.join(CLIENT_BUILD_DIR, 'index.html')) as f:
        return web.Response(text=f.read(), content_type='text/html')


@sio.on('connect', namespace='/cam')
def connect(sid, environ):
    logger.warning('Connection established: {sid} from {origin}.'.format(
        sid=sid, origin=environ.get('HTTP_ORIGIN', 'unknown origin')
    ))

    if not app['frame_manager'].is_started:
        logger.warning('Starting camera...')
        app['frame_manager'].start()

    app['client'] += 1


@sio.on('shoot', namespace='/cam')
async def message(sid):
    manager = app['frame_manager']
    img = manager.shoot()
    set_img_path(img)

    logger.debug('Sending image update for {filename} thumb'.format(filename=img.filename))
    await sio.emit('image', img.__dict__, room=sid, namespace='/cam')


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
            thumb = manager.make_thumb()
            set_thumb_path(thumb)

            logger.debug('Sending frame update for {filename} thumb'.format(filename=thumb.filename))
            await sio.emit('thumb', thumb.__dict__, namespace='/cam')


def run(driver=Drivers.RPI, **kwargs):
    app['frame_rate'] = 6
    app['client'] = 0

    app['frame_manager'] = get_frame_manager(driver)

    app.router.add_static('/cam_data', app['frame_manager'].path, show_index=True)
    app.router.add_get('/', index)
    app.router.add_static('/', CLIENT_BUILD_DIR)

    sio.start_background_task(stream_thumbs)
    web.run_app(app, **kwargs)

    if app['frame_manager'].is_started:
        app['frame_manager'].stop()


if __name__ == '__main__':
    run()
