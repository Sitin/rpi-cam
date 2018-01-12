import logging
import os
import sys


APP_DIR = os.path.dirname(os.path.realpath(__file__))
SERVER_DIR = os.path.dirname(APP_DIR)
PROJECT_DIR = os.path.dirname(SERVER_DIR)
CLIENT_BUILD_DIR = os.path.join(PROJECT_DIR, 'client', 'rpi-cam-web', 'build')
CAM_DATA_DIR = os.path.join(SERVER_DIR, 'cam_data')


def get_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    info = logging.StreamHandler(stream=sys.stdout)
    error = logging.StreamHandler(stream=sys.stderr)
    error.setLevel(logging.ERROR)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    info.setFormatter(formatter)
    error.setFormatter(formatter)

    logger.addHandler(info)
    logger.addHandler(error)

    return logger
