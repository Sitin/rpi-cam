import abc
import datetime
import glob
from PIL import Image
import os
import shutil
import uuid

from rpi_cam.tools import get_logger


DEFAULT_PREVIEW_RESOLUTION = '320x240'
DEFAULT_THUMBNAIL_BOUNDS = (320, 240)
DEFAULT_MAX_PREVIEWS_COUNT = 24 * 5
DEFAULT_LATEST_IMAGES_COUNT = 6

default_logger = get_logger('rpi_cam.capture.frame_manager.default')


def get_preview_resolution(raw_value):
    if type(raw_value) is str:
        pair = raw_value.split('x')
        return int(pair[0]), int(pair[1])
    else:
        return raw_value


class ImageError(OSError):
    pass


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


class FPSCounter(object):
    def __init__(self, frame_resolution=10):
        self.frame_resolution = frame_resolution
        self.ticks = 0
        self.key_frame = 0
        self.key_frame_time = None
        self.fps = 0

    def reset(self):
        self.key_frame = self.ticks
        self.key_frame_time = None
        self.fps = 0

    def tick(self):
        self.ticks += 1
        ticks_delta = self.ticks - self.key_frame

        if self.key_frame_time is None:
            self.key_frame_time = datetime.datetime.now()

        if ticks_delta >= self.frame_resolution:
            now = datetime.datetime.now()
            delta = now - self.key_frame_time
            time_delta = delta.total_seconds()

            if time_delta > 0:
                self.fps = ticks_delta / time_delta
                self.key_frame_time = now
                self.key_frame = self.ticks


class FrameManager(object):
    THUMB_PREFIX = '__thumb__'
    
    def __init__(self, path,
                 preview_resolution=DEFAULT_PREVIEW_RESOLUTION,
                 thumbnail_bounds=DEFAULT_THUMBNAIL_BOUNDS,
                 url_prefix='',
                 max_previews_count=DEFAULT_MAX_PREVIEWS_COUNT,
                 logger=default_logger,
                 beep_on_shoot=True,
                 **kwargs
                 ):
        self.logger = logger
        self.path = path
        self.preview_path = os.path.join(path, 'previews')
        self.gallery_path = os.path.join(path, 'gallery')
        self.preview_resolution = get_preview_resolution(preview_resolution)
        self.thumbnail_bounds = thumbnail_bounds
        self.image_resolution = None
        self.extension = 'jpg'
        self.format = 'jpeg'
        self.camera = None
        self.is_started = False
        self.url_prefix = url_prefix
        self.max_previews_count = max_previews_count
        self._previews = 0
        self.beep_on_shoot = beep_on_shoot

        self.fps_counter = FPSCounter()

        os.makedirs(self.path, exist_ok=True)
        self.reset_previews()
        self.move_previous_session_to_gallery()

        self.logger.debug('Extra arguments will be processed by ancestors: {kwargs}'.format(kwargs=kwargs))

    def _get_preview_img_data(self, filename):
        return ImageData('previews/' + os.path.basename(filename),
                         self.preview_resolution,
                         url_prefix=self.url_prefix)

    def get_latest_previews(self, count):
        previews = glob.glob(os.path.join(self.preview_path, '*.%s' % self.extension))
        self.logger.debug('Loaded latest previews: {files}'.format(files=previews))

        return sorted(previews, key=os.path.getctime)[count:]

    def get_latest_images(self, count=DEFAULT_LATEST_IMAGES_COUNT):
        images = glob.glob(os.path.join(self.path, '*.%s' % self.extension))
        images = [img for img in images if not os.path.basename(img).startswith(self.THUMB_PREFIX)]
        latest_images = sorted(images, key=os.path.getctime, reverse=True)[:count]

        self.logger.debug('Loaded latest images: {files}'.format(files=latest_images))

        return [self.get_image_data(img) for img in latest_images]

    def reset_previews(self):
        self.logger.info('Resetting previews.')

        try:
            shutil.rmtree(self.preview_path)
        except FileNotFoundError:
            pass

        os.makedirs(self.preview_path, exist_ok=True)

    def move_previous_session_to_gallery(self):
        self.logger.info('Saving previous session to gallery.')

        os.makedirs(self.gallery_path, exist_ok=True)

        images = glob.glob(os.path.join(self.path, '*.%s' % self.extension))
        for img in images:
            shutil.move(img, self.gallery_path)

    def truncate_previews(self):
        if self._previews < self.max_previews_count:
            return

        self.logger.debug('Truncating previews to maximum count of {count}...'.format(
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

    def get_thumbnail_filename(self, filename):
        """Prepends file's basename with `self.THUMB_PREFIX` (__thumb__ by default)"""
        return os.path.join(os.path.dirname(filename),
                            self.THUMB_PREFIX + os.path.basename(filename))

    def get_image_data(self, filename, thumbnail_data=None):
        try:
            if thumbnail_data is None:
                thumbnail_data = self.get_img_thumbnail_data(filename)

            if self.image_resolution is None:
                image = Image.open(filename)
                resolution = image.size
            else:
                resolution = self.image_resolution

            return ImageData(os.path.basename(filename),
                             resolution,
                             url_prefix=self.url_prefix,
                             thumbnail=thumbnail_data)
        except OSError:
            raise ImageError('Can not get image data for file: {filename}'.format(filename=filename))

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

        self.fps_counter.tick()

        self.logger.debug('Created preview #{no}: "{filename}"'.format(no=self._previews, filename=filename))

        return self._get_preview_img_data(filename)

    def _preview(self, filename):
        thumb = self.get_preview()

        if thumb is not None:
            self.write_img(filename, thumb)

    def make_thumbnail(self, filename):
        try:
            thumb_filename = self.get_thumbnail_filename(filename)
            img = Image.open(filename)
            img.thumbnail(self.thumbnail_bounds, Image.ANTIALIAS)
            img.save(thumb_filename)
            return ImageData(os.path.basename(thumb_filename), img.size)
        except OSError:
            self.logger.error('Can not create thumbnail for {filename}'.format(filename=filename))
            return None

    def get_img_thumbnail_data(self, filename):
        thumb_filename = self.get_thumbnail_filename(filename)
        try:
            thumbnail = Image.open(thumb_filename)
            return ImageData(os.path.basename(thumb_filename),
                             thumbnail.size,
                             url_prefix=self.url_prefix)
        except FileNotFoundError:
            self.logger.warning('Creating missing thumbnail for image {filename}.'.format(
                filename=os.path.basename(filename)
            ))
            return self.make_thumbnail(filename)

    def shoot(self):
        filename = self.get_image_filename()
        self._shoot(filename)
        thumbnail_data = self.make_thumbnail(filename)

        self.logger.warning('Image "{filename}" saved.'.format(filename=filename))
        self.beep()

        return self.get_image_data(filename, thumbnail_data)

    def beep(self):
        if self.beep_on_shoot:
            self._beep()

    def _beep(self):
        pass

    def _shoot(self, filename):
        img = self.get_image()

        if img is not None:
            self.write_img(filename, img)

    def report_state(self):
        return {
            'is_critical': False,
            'data': {}
        }

    @abc.abstractmethod
    def start(self):
        self.is_started = True
        self.fps_counter.reset()

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
