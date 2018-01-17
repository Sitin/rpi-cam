from io import BytesIO
import subprocess

import picamera
from PIL import Image

from rpi_cam.tools import exec_time_patcher
from rpi_cam.capture.frame_manager import FrameManager
from rpi_cam.capture.rpi_capture.picamera_options import DEFAULT_SENSOR_MODE, get_picamera_options


class PiCameraFrameManager(FrameManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        picamera_options = get_picamera_options(kwargs.get('sensor_mode', DEFAULT_SENSOR_MODE))

        self.preview_sensor_mode = kwargs.get('preview_sensor_mode', picamera_options['preview_sensor_mode'])
        self.sensor_mode = kwargs.get('sensor_mode', picamera_options['sensor_mode'])
        self.framerate = kwargs.get('framerate', picamera_options['framerate'])
        self.resolution = kwargs.get('resolution', picamera_options['resolution'])
        self.fullscreen = kwargs.get('fullscreen', picamera_options['fullscreen'])
        self.window = kwargs.get('window', picamera_options['window'])

        self._preview, self.rpi_preview_exec_measures = exec_time_patcher(self._preview)

    def start(self, sensor_mode=None):
        super().start()

        if sensor_mode is None:
            sensor_mode = self.preview_sensor_mode

        self.camera = picamera.PiCamera(sensor_mode=sensor_mode,
                                        resolution=self.resolution,
                                        framerate=self.framerate,
                                        )

        self.logger.info('Create RPi camera instance: {camera} with sensor mode {sensor_mode}.'.format(
            camera=repr(self.camera),
            sensor_mode=sensor_mode,
        ))

        self.camera.start_preview()
        self.camera.preview.fullscreen = self.fullscreen
        if self.window is not None:
            self.camera.preview.window = self.window

        self.logger.info('Starting RPi camera preview with: {preview}.'.format(
            preview=repr(self.camera.preview)
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

    def _capture_image(self, filename):
        self.camera.capture(filename)
        self.image_resolution = Image.open(filename).size

    def _shoot(self, filename):
        if not self.sensor_mode == self.preview_sensor_mode:
            self.stop()
            self.start(self.sensor_mode)

            self._capture_image(filename)

            self.stop()
            self.start()
        else:
            self._capture_image(filename)

    def report_state(self):
        state = super().report_state()

        state['data']['temperature'] = subprocess.getoutput('/opt/vc/bin/vcgencmd measure_temp')
        state['data']['rpi_preview_time'] = '%08.6f' % self.rpi_preview_exec_measures.avg()
        state['data']['driver'] = 'PiCamera'

        self.rpi_preview_exec_measures.truncate()

        return state

    def write_img(self, filename, img):
        img.save(filename)

    def stop(self):
        super().stop()
        self.camera.close()
        self.camera = None
        self.image_resolution = None

    def _beep(self):
        subprocess.call(['timeout', '0.1s', 'speaker-test', '-t', 'sine', '-f', '600'])
