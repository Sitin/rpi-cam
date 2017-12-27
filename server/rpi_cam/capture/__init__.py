from rpi_cam.capture.frame_manager import FrameManager


class Drivers(object):
    OPENCV = 'opencv'
    RPI = 'rpi'


def get_frame_manager(name: str, *args, **kwargs) -> FrameManager:
    if name == Drivers.OPENCV:
        from rpi_cam.capture.opencv_capture.opencv_frame_manager import OpenCVFrameManager
        return OpenCVFrameManager(*args, **kwargs)
    if name == Drivers.RPI:
        from rpi_cam.capture.rpi_capture.opencv_frame_manager import PiCameraFrameManager
        return PiCameraFrameManager(*args, **kwargs)
    else:
        raise ValueError('Driver is not supported: {name}.'.format(name=name))
