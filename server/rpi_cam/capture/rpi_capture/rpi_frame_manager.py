from io import BytesIO

import picamera
from Pillow import Image

from rpi_cam.capture.frame_manager import FrameManager


class PiCameraFrameManager(FrameManager):
    def start(self):
        super().start()
        self.cap = picamera.PiCamera()
        self.cap.start_preview()

    def get_frame(self):
        stream = BytesIO()
        self.cap.capture(stream, format='jpeg')
        stream.seek(0)
        image = Image.open(stream)
        self.image_resolution = image.size
        return image

    def get_thumb(self):
        stream = BytesIO()
        self.cap.capture(stream, format='jpeg', resize=self.thumb_resolution)
        stream.seek(0)
        return Image.open(stream)

    def write_img(self, filename, img):
        img.save(filename, 'JPEG')

    def stop(self):
        super().stop()
        self.cap.stop_preview()
        self.cap = None
        self.image_resolution = None
