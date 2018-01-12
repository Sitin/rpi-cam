from io import BytesIO

import picamera
from PIL import Image

from rpi_cam.capture.frame_manager import FrameManager


RPI_DEFAULT_ARGS = {
    'sensor_mode': 4,
    'framerate': 15,
    'resolution': '1640x1232',
    'fullscreen': False,
    'window': (10, 10, 320, 240),
}


class PiCameraFrameManager(FrameManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sensor_mode = kwargs.get('sensor_mode', RPI_DEFAULT_ARGS['sensor_mode'])
        self.framerate = kwargs.get('framerate', RPI_DEFAULT_ARGS['framerate'])
        self.resolution = kwargs.get('resolution', RPI_DEFAULT_ARGS['resolution'])
        self.fullscreen = kwargs.get('fullscreen', RPI_DEFAULT_ARGS['fullscreen'])
        self.window = kwargs.get('window', RPI_DEFAULT_ARGS['window'])

    def start(self):
        super().start()
        self.camera = picamera.PiCamera(sensor_mode=self.sensor_mode,
                                        resolution=self.resolution,
                                        framerate=self.framerate,
                                        )

        self.logger.info('Create RPi camera instance: {camera}'.format(
            camera=self.camera
        ))

        self.camera.start_preview()
        self.camera.preview.fullscreen = self.fullscreen
        if self.window is not None:
            self.camera.preview.window = self.window

        self.logger.info('Starting RPi camera preview with: {preview}'.format(
            preview=self.camera.preview
        ))

    def get_image(self):
        stream = BytesIO()
        self.camera.capture(stream, format=self.format)
        stream.seek(0)
        image = Image.open(stream)
        self.image_resolution = image.size
        return image

    def get_preview(self):
        stream = BytesIO()
        self.camera.capture(stream, format=self.format, resize=self.preview_resolution)
        stream.seek(0)
        return Image.open(stream)

    def _preview(self, filename):
        self.camera.capture(filename, resize=self.preview_resolution)

    def _shoot(self, filename):
        self.camera.capture(filename)
        self.image_resolution = Image.open(filename).size

    def write_img(self, filename, img):
        img.save(filename)

    def stop(self):
        super().stop()
        self.camera.close()
        self.camera = None
        self.image_resolution = None
