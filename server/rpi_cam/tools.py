import logging
import os


APP_DIR = os.path.dirname(os.path.realpath(__file__))
SERVER_DIR = os.path.dirname(APP_DIR)
PROJECT_DIR = os.path.dirname(SERVER_DIR)
CLIENT_BUILD_DIR = os.path.join(PROJECT_DIR, 'client', 'rpi-cam-web', 'build')
CAM_DATA_DIR = os.path.join(SERVER_DIR, 'cam_data')


def get_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    ch = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger
