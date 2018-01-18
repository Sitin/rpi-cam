import pygame.image
import pygame.camera
from PIL import Image

from rpi_cam.capture.frame_manager import FrameManager


DEFAULT_TARGET_RESOLUTION = (1640, 1232)


class PyGameFrameManager(FrameManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.target_resolution = self.image_resolution
        if self.target_resolution is None:
            self.target_resolution = DEFAULT_TARGET_RESOLUTION

        pygame.camera.init()

    def start(self, image_size=None):
        super().start()

        if image_size is None:
            image_size = self.target_resolution

        self.camera = pygame.camera.Camera(pygame.camera.list_cameras()[0], image_size)
        self.camera.start()

    def _get_image_from_camera(self):
        if self.camera is None:
            return None

        surface = self.camera.get_image()
        imgstr = pygame.image.tostring(surface, 'RGB')
        image = Image.fromstring('RGB', surface.get_size(), imgstr)

        return image

    def get_image(self):
        self.stop()
        self.start(image_size=self.target_resolution)

        image = self._get_image_from_camera()
        self.image_resolution = image.size

        self.stop()
        self.start(image_size=self.preview_resolution)

        return image

    def get_preview(self):
        return self._get_image_from_camera()

    def report_state(self):
        state = super().report_state()

        state['data']['driver'] = 'PyGame'

        return state

    def write_img(self, filename, img):
        img.save(filename)

    def _preview(self, filename):
        image = self.camera.get_image()
        pygame.image.save(image, filename)

    def _shoot(self, filename):
        self.stop()
        self.start(image_size=self.target_resolution)

        image = self.camera.get_image()
        pygame.image.save(image, filename)
        self.image_resolution = image.get_size()

        self.stop()
        self.start(image_size=self.preview_resolution)

    def stop(self):
        super().stop()
        self.camera.stop()
        self.camera = None
        self.image_resolution = None
