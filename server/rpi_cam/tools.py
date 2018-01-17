import logging
import os
import sys
import time


APP_DIR = os.path.dirname(os.path.realpath(__file__))
SERVER_DIR = os.path.dirname(APP_DIR)
PROJECT_DIR = os.path.dirname(SERVER_DIR)
CLIENT_BUILD_DIR = os.path.join(PROJECT_DIR, 'client', 'rpi-cam-web', 'build')
CAM_DATA_DIR = os.path.join(SERVER_DIR, 'cam_data')


class SocketIOHandler(logging.Handler):
    def __init__(self, sio, namespace, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sio = sio
        self.namespace = namespace
        self.sid = None

    async def emit_async(self, record):
        await self.sio.emit(
            'log',
            {
                'level': record.levelname,
                'levelNo': record.levelno,
                'title': '{name} - {module}.{func_name}'.format(
                  name=record.name, module=record.module, func_name=record.funcName),
                'text': self.formatter.format(record),
            },
            namespace=self.namespace,
        )

    def emit(self, record):
        self.sio.start_background_task(self.emit_async, record)


def get_logger(name, level=logging.INFO, sio=None, namespace=None):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    info_handler = logging.StreamHandler(stream=sys.stdout)
    error_handler = logging.StreamHandler(stream=sys.stderr)
    error_handler.setLevel(logging.ERROR)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    info_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)

    logger.addHandler(info_handler)
    logger.addHandler(error_handler)

    if sio:
        sio_handler = SocketIOHandler(sio, namespace)
        sio_handler.setFormatter(formatter)
        logger.addHandler(sio_handler)

    return logger


class TimeMeasures(object):
    def __init__(self, max_size=10):
        self.max_size = max_size
        self.measures = []

    def append(self, item):
        self.measures.append(item)

    def avg(self):
        if len(self.measures) > 0:
            return sum(self.measures) / len(self.measures)
        else:
            return -1

    def reset(self):
        self.measures = []

    def truncate(self):
        if len(self.measures) > self.max_size:
            self.measures = self.measures[int(self.max_size / 2):]


def exec_time_patcher(fn):
    measures = TimeMeasures()

    def decorator_fn(*args, **kwargs):
        start = time.time()

        result = fn(*args, **kwargs)

        end = time.time()
        measures.append(end - start)

        return result

    return decorator_fn, measures
