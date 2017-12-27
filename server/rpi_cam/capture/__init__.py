import enum

from rpi_cam.capture.frame_manager import FrameManager


class Drivers(enum.Enum):
    OPENCV = 1
    RPI = 2


def get_frame_manager(name: Drivers, *args, **kwargs) -> FrameManager:
    if name == Drivers.OPENCV:
        from rpi_cam.capture.opencv_capture.opencv_frame_manager import OpenCVFrameManager
        return OpenCVFrameManager(*args, **kwargs)
    else:
        raise ValueError('Driver is not supported: {name}.'.format(name=name))
