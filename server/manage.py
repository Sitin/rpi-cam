import os
import subprocess

from manager import Manager
from jinja2 import Template

import rpi_cam.server
from rpi_cam.capture import Drivers
from rpi_cam.tools import SERVER_DIR, CAM_DATA_DIR


manager = Manager()

NGINX_CONF_TEMPLATE = os.path.join(SERVER_DIR, 'nginx.conf.tmpl')
DEFAULT_NGINX_CONF_FILE = os.path.join(SERVER_DIR, 'nginx.conf')

DEFAULT_SOCKET = '/tmp/rpi_cam.sock'
DEFAULT_RPI_CAM_PORT = 8080
DEFAULT_FRAME_RATE = 24

NGINX_DEFAULTS = {
    'pid': '/tmp/nginx-rpi_cam.pid',
    'port': 8000,
}


@manager.command
def runserver(port=DEFAULT_RPI_CAM_PORT,
              frame_rate=DEFAULT_FRAME_RATE,
              path=DEFAULT_SOCKET,
              host=None,
              driver=Drivers.RPI):
    """Runs server at <port> (default is 8080)"""
    return rpi_cam.server.run(port=int(port), frame_rate=frame_rate,
                              cam_data_dir=CAM_DATA_DIR,
                              path=path, host=host, driver=driver)


@manager.command
def nginx_conf(path=DEFAULT_NGINX_CONF_FILE,
               pid=NGINX_DEFAULTS['pid'],
               content_root=SERVER_DIR,
               port=NGINX_DEFAULTS['port'],
               socket=DEFAULT_SOCKET,
               rpi_cam_port=DEFAULT_RPI_CAM_PORT,
               ):
    """Generates nginx config"""
    with open(NGINX_CONF_TEMPLATE) as tmpl:
        template = Template(tmpl.read())
        config = template.render(pid=pid, content_root=content_root, socket=socket,
                                 port=port, rpi_cam_port=rpi_cam_port)

        with open(path, 'w') as conf:
            conf.write(config)


@manager.command
def nginx(conf_file=DEFAULT_NGINX_CONF_FILE):
    """Runs Nginx server in foreground"""
    subprocess.run(['nginx', '-c', conf_file])


if __name__ == '__main__':
    manager.main()
