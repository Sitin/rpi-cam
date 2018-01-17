_sensor_mode_to_resolution = {
    0: None,
    1: '1920x1080',
    2: '3280x2464',
    3: '3280x2464',
    4: '1640x1232',
    5: '1640x922',
    6: '1280x720',
    7: '640x480',
}

_sensor_mode_to_framerate = {
    0: None,
    1: 24,  # Maximum is 30
    2: 10,  # Maximum is 15
    3: 10,  # Maximum is 15
    4: 15,  # Maximum is 40
    5: 15,  # Maximum is 40
    6: 30,  # Maximum is 90
    7: 30,  # Maximum is 90
}


DEFAULT_SENSOR_MODE = 4
DEFAULT_PREVIEW_SENSOR_MODE = 7


def get_picamera_options(sensor_mode=DEFAULT_SENSOR_MODE):
    return {
        'sensor_mode': sensor_mode,
        'preview_sensor_mode': DEFAULT_PREVIEW_SENSOR_MODE,
        'framerate': _sensor_mode_to_framerate[sensor_mode],
        'resolution': _sensor_mode_to_resolution[sensor_mode],
        'fullscreen': False,
        'window': (10, 10, 320, 240),
    }


RPI_DEFAULT_OPTIONS = get_picamera_options()
