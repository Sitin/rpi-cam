import os

from aiohttp import web
import socketio

from rpi_cam.tools import get_logger, PROJECT_DIR
from rpi_cam.capture import get_frame_manager, Drivers, FrameManager


logger = get_logger('rpi_cam.server')

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)


def get_img_src(filename):
    return '/cam_data/%s' % filename


def get_thumb_src(filename):
    return '/cam_data/thumbs/%s' % filename


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
    manager: FrameManager = app['frame_manager']
    filename = manager.shoot()

    await sio.emit('image', {
        'src': get_img_src(filename),
        'ratio': manager.image_resolution[0] / manager.image_resolution[1],
    }, room=sid, namespace='/cam')


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
    manager: FrameManager = app['frame_manager']

    while True:
        await sio.sleep(1 / app['frame_rate'])

        if manager.is_started:
            app['frame_count'] += 1
            thumb_filename = manager.make_thumb()
            thumb_src = get_thumb_src(thumb_filename)

            logger.debug('Sending frame update for {thumb_name} thumb'.format(thumb_name=thumb_filename))
            await sio.emit('thumb', {
                'src': thumb_src,
                'ratio': manager.thumb_resolution[0] / manager.thumb_resolution[1],
            }, namespace='/cam')


def run(driver=Drivers.RPI, **kwargs):
    app['frame_rate'] = 6
    app['client'] = 0

    app['frame_manager'] = get_frame_manager(driver)

    app.router.add_static('/cam_data', app['frame_manager'].path, show_index=True)
    app.router.add_static('/', os.path.join(PROJECT_DIR, 'client', 'rpi-cam-web', 'build'))

    sio.start_background_task(stream_thumbs)
    web.run_app(app, **kwargs)

    app['frame_manager'].stop()


if __name__ == '__main__':
    run()
