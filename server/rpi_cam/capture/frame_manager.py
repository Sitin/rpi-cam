import abc
import datetime
import glob
from PIL import Image
import os
import shutil
import uuid

from rpi_cam.tools import get_logger, SERVER_DIR


DEFAULT_PATH = os.path.join(SERVER_DIR, 'cam_data')
DEFAULT_PREVIEW_RESOLUTION = (320, 240)
DEFAULT_THUMBNAIL_BOUNDS = (320, 240)
DEFAULT_MAX_PREVIEWS_COUNT = 24 * 5

logger = get_logger('rpi_cam.capture.frame_manager')


class ImageData:
    def __init__(self, filename, resolution, thumbnail=None, url_prefix=''):
        self.filename = filename
        self.resolution = resolution
        self.ratio = resolution[0] / resolution[1]
        self.thumbnail = thumbnail
        self.url_prefix = ''
        self.set_url_prefix(url_prefix)

    def set_url_prefix(self, url_prefix):
        self.url_prefix = url_prefix
        if self.thumbnail is not None:
            self.thumbnail.set_url_prefix(url_prefix)

    @property
    def src(self):
        return '{path}/{filename}'.format(path=self.url_prefix, filename=self.filename)

    @property
    def __dict__(self):
        data = {
            'src': self.src,
            'resolution': self.resolution,
            'ratio': self.ratio,
        }

        if self.thumbnail is not None:
            data['thumbnail'] = self.thumbnail.__dict__

        return data


class FrameManager(object):
    def __init__(self, path=DEFAULT_PATH,
                 preview_resolution=DEFAULT_PREVIEW_RESOLUTION,
                 thumbnail_bounds=DEFAULT_THUMBNAIL_BOUNDS,
                 url_prefix='',
                 max_previews_count=DEFAULT_MAX_PREVIEWS_COUNT):
        self.path = path
        self.preview_path = os.path.join(path, 'previews')
        self.preview_resolution = preview_resolution
        self.thumbnail_bounds = thumbnail_bounds
        self.image_resolution = None
        self.extension = 'jpg'
        self.format = 'jpeg'
        self.camera = None
        self.is_started = False
        self.url_prefix = url_prefix
        self.max_previews_count = max_previews_count
        self._previews = 0

        os.makedirs(self.path, exist_ok=True)
        self.reset_previews()

    def _get_preview_img_data(self, filename):
        return ImageData('previews/' + os.path.basename(filename),
                         self.preview_resolution,
                         url_prefix=self.url_prefix)

    def get_latest_previews(self, count):
        previews = glob.glob(os.path.join(self.preview_path, '*.%s' % self.extension))
        return sorted(previews, key=os.path.getctime)[count:]

    def reset_previews(self):
        try:
            shutil.rmtree(self.preview_path)
        except FileNotFoundError:
            pass
        os.makedirs(self.preview_path, exist_ok=True)

    def truncate_previews(self):
        if self._previews < self.max_previews_count:
            return

        logger.info('Truncating previews to maximum count of {count}...'.format(
            count=self.max_previews_count
        ))

        previews = glob.glob(os.path.join(self.preview_path, '*.%s' % self.extension))
        oldest = sorted(previews, key=os.path.getctime)[:-self.max_previews_count // 2]

        for filename in oldest:
            os.remove(filename)

        self._previews = self.max_previews_count // 2

    def get_image_filename(self):
        return os.path.join(self.path, '{name}.{extension}'.format(
            name='{datetime}-{uuid}'.format(
                datetime=datetime.datetime.now().isoformat(),
                uuid=str(uuid.uuid4()),
            ),
            extension=self.extension
        ))

    @staticmethod
    def get_thumbnail_filename(filename):
        """Prepends file's basename with __thumb__"""
        return os.path.join(os.path.dirname(filename),
                            '__thumb__' + os.path.basename(filename))

    def get_preview_filename(self):
        return os.path.join(self.preview_path, '{name}.{extension}'.format(
            name=str(uuid.uuid4()),
            extension=self.extension
        ))

    def preview(self):
        self.truncate_previews()
        filename = self.get_preview_filename()
        self._preview(filename)
        self._previews += 1
        return self._get_preview_img_data(filename)

    def _preview(self, filename):
        thumb = self.get_preview()

        if thumb is not None:
            self.write_img(filename, thumb)

    def make_thumbnail(self, filename):
        thumb_filename = self.get_thumbnail_filename(filename)
        img = Image.open(filename)
        img.thumbnail(self.thumbnail_bounds, Image.ANTIALIAS)
        img.save(thumb_filename)
        return thumb_filename, img.size

    def shoot(self):
        filename = self.get_image_filename()
        self._shoot(filename)
        thumb_filename, thumbnail_resolution = self.make_thumbnail(filename)

        image_data = ImageData(os.path.basename(filename),
                               self.image_resolution,
                               url_prefix=self.url_prefix,
                               thumbnail=ImageData(os.path.basename(thumb_filename),
                                                   thumbnail_resolution))
        logger.warning('Image "{filename}" saved.'.format(filename=image_data.filename))
        return image_data

    def _shoot(self, filename):
        img = self.get_image()

        if img is not None:
            self.write_img(filename, img)

    @abc.abstractmethod
    def start(self):
        self.is_started = True

    @abc.abstractmethod
    def get_image(self):
        pass

    @abc.abstractmethod
    def get_preview(self):
        pass

    @abc.abstractmethod
    def write_img(self, filename, img):
        pass

    @abc.abstractmethod
    def stop(self):
        self.is_started = False
