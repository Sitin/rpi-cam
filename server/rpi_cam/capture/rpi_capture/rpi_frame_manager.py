from io import BytesIO

import picamera
from PIL import Image

from rpi_cam.capture.frame_manager import FrameManager


class PiCameraFrameManager(FrameManager):
    DELAY_AFTER_STOP = 2

    def start(self):
        super().start()
        self.camera = picamera.PiCamera()
        self.camera.start_preview()

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
