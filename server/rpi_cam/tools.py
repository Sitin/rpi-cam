import logging
import os


APP_DIR = os.path.dirname(os.path.realpath(__file__))
SERVER_DIR = os.path.dirname(APP_DIR)
PROJECT_DIR = os.path.dirname(SERVER_DIR)


def get_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger
