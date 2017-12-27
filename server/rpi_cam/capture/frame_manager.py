import abc
import datetime
import glob
import os
import shutil
import uuid

from rpi_cam.tools import get_logger, SERVER_DIR


DEFAULT_PATH = os.path.join(SERVER_DIR, 'cam_data')
DEFAULT_THUMB_RESOLUTION = (320, 240)

logger = get_logger('rpi_cam.capture.frame_manager')


class FrameManager(object):
    def __init__(self, path=DEFAULT_PATH, thumb_resolution=DEFAULT_THUMB_RESOLUTION):
        self.path = path
        self.thumbs_path = os.path.join(path, 'thumbs')
        self.thumb_resolution = thumb_resolution
        self.image_resolution = None
        self.extension = 'jpg'
        self.format = 'jpeg'
        self.cap = None
        self.is_started = False

        os.makedirs(self.path, exist_ok=True)
        self.reset_thumbs()

    def get_latest_img(self):
        list_of_files = glob.glob(os.path.join(self.path, '*.%s' % self.extension))
        latest_file = max(list_of_files, key=os.path.getctime)
        return latest_file

    def reset_thumbs(self):
        try:
            shutil.rmtree(self.thumbs_path)
        except FileNotFoundError:
            pass
        os.makedirs(self.thumbs_path, exist_ok=True)

    def get_filename(self):
        return os.path.join(self.path, '{name}.{extension}'.format(
            name='{datetime}-{uuid}'.format(
                datetime=datetime.datetime.now().isoformat(),
                uuid=str(uuid.uuid4()),
            ),
            extension=self.extension
        ))

    def get_thumb_filename(self):
        return os.path.join(self.thumbs_path, '{name}.{extension}'.format(
            name=str(uuid.uuid4()),
            extension=self.extension
        ))

    def make_thumb(self):
        filename = self.get_thumb_filename()
        self._make_thumb(filename)
        return os.path.basename(filename)

    def _make_thumb(self, filename):
        thumb = self.get_thumb()

        if thumb is not None:
            self.write_img(filename, thumb)

    def shoot(self):
        filename = self.get_filename()
        self._shoot(filename)
        return os.path.basename(filename)

    def _shoot(self, filename):
        img = self.get_frame()

        if img is not None:
            self.write_img(filename, img)

    @abc.abstractmethod
    def start(self):
        self.is_started = True

    @abc.abstractmethod
    def get_frame(self):
        pass

    @abc.abstractmethod
    def get_thumb(self):
        pass

    @abc.abstractmethod
    def write_img(self, filename, img):
        pass

    @abc.abstractmethod
    def stop(self):
        self.is_started = False
