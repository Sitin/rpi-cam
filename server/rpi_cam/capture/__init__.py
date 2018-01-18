from rpi_cam.capture.frame_manager import FrameManager


class Drivers(object):
    OPENCV = 'opencv'
    RPI = 'rpi'
    PYGAME = 'pygame'


def get_frame_manager(name: str, *args, **kwargs):
    if name == Drivers.OPENCV:
        from rpi_cam.capture.opencv_capture.opencv_frame_manager import OpenCVFrameManager
        return OpenCVFrameManager(*args, **kwargs)
    if name == Drivers.RPI:
        from rpi_cam.capture.rpi_capture.rpi_frame_manager import PiCameraFrameManager
        return PiCameraFrameManager(*args, **kwargs)
    if name == Drivers.PYGAME:
        from rpi_cam.capture.pygame_capture.pygame_frame_manager import PyGameFrameManager
        return PyGameFrameManager(*args, **kwargs)
    else:
        raise ValueError('Driver is not supported: {name}.'.format(name=name))
