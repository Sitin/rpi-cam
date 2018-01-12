#!/usr/bin/env python3

import os
import shutil
import subprocess
import urllib.request

from manager import Manager
from jinja2 import Template

import rpi_cam.server
from rpi_cam.capture import Drivers
from rpi_cam.tools import SERVER_DIR, CAM_DATA_DIR, CLIENT_BUILD_DIR, PROJECT_DIR


manager = Manager()

NGINX_CONF_TEMPLATE = os.path.join(SERVER_DIR, 'nginx.conf.tmpl')
DEFAULT_NGINX_CONF_FILE = os.path.join(SERVER_DIR, 'nginx.conf')

SUPERVISOR_CONF_TEMPLATE = os.path.join(SERVER_DIR, 'rpi_cam-supervisor.conf.tmpl')
DEFAULT_SUPERVISOR_CONF_FILE = os.path.join(SERVER_DIR, 'rpi_cam-supervisor.conf')

DEFAULT_SOCKET = '/tmp/rpi_cam.sock'
DEFAULT_RPI_CAM_PORT = 8080
DEFAULT_FRAME_RATE = 24

NGINX_DEFAULTS = {
    'pid': '/tmp/nginx-rpi_cam.pid',
    'port': 8000,
}

SUPERVISOR_DEFAULTS = {
    'command': os.path.join(SERVER_DIR, 'manage.py') + ' runserver',
    'args': [
        '--log-level INFO',
    ],
}

LATEST_CLIENT_BUILD_URL = 'https://www.dropbox.com/s/khbgbpa7xxeqgfj/rpi_cam-client-build.tar.gz?dl=1'


@manager.command
def runserver(port=DEFAULT_RPI_CAM_PORT,
              frame_rate=DEFAULT_FRAME_RATE,
              path=DEFAULT_SOCKET,
              host=None,
              driver=Drivers.RPI,
              client_build_dir=CLIENT_BUILD_DIR,
              cam_data_dir=CAM_DATA_DIR,
              log_level='INFO',
              ):
    """Runs server at <port> (default is 8080)"""
    return rpi_cam.server.run(port=int(port), frame_rate=frame_rate,
                              cam_data_dir=cam_data_dir, client_build_dir=client_build_dir,
                              path=path, host=host, driver=driver,
                              log_level=log_level,
                              )


@manager.command
def nginx_conf(path=DEFAULT_NGINX_CONF_FILE,
               pid=NGINX_DEFAULTS['pid'],
               content_root=SERVER_DIR,
               client_build_dir=CLIENT_BUILD_DIR,
               port=NGINX_DEFAULTS['port'],
               socket=DEFAULT_SOCKET,
               rpi_cam_port=DEFAULT_RPI_CAM_PORT,
               as_service=False,
               server_name='rpi-cam.ziatin.me',
               user='www-data',
               ):
    """Generates nginx config"""
    with open(NGINX_CONF_TEMPLATE) as tmpl:
        template = Template(tmpl.read())
        config = template.render(pid=pid, content_root=content_root, socket=socket,
                                 port=port, rpi_cam_port=rpi_cam_port, client_build_dir=client_build_dir,
                                 as_service=as_service, server_name=server_name, user=user,
                                 )

        with open(path, 'w') as conf:
            conf.write(config)


@manager.command
def supervisor_conf(path=DEFAULT_SUPERVISOR_CONF_FILE,
                    command=SUPERVISOR_DEFAULTS['command'],
                    args=SUPERVISOR_DEFAULTS['args'],
                    log_dir=PROJECT_DIR,
                    ):
    """Generates nginx config"""
    with open(SUPERVISOR_CONF_TEMPLATE) as tmpl:
        template = Template(tmpl.read())
        config = template.render(command=command, args=' '.join(args), project_dir=PROJECT_DIR, log_dir=log_dir)

        with open(path, 'w') as conf:
            conf.write(config)


@manager.command
def nginx(conf_file=DEFAULT_NGINX_CONF_FILE):
    """Runs Nginx server in foreground"""
    subprocess.run(['nginx', '-c', conf_file])


@manager.command
def get_client(url=LATEST_CLIENT_BUILD_URL, path=CLIENT_BUILD_DIR, tmp_dir='/tmp'):
    """Generates Supervisor config"""
    tmp_arc_path = os.path.join(tmp_dir, 'rpi_cam-client.tgz')
    urllib.request.urlretrieve(url, tmp_arc_path)
    shutil.rmtree(path, ignore_errors=True)
    subprocess.run(['tar', '-xvzf', tmp_arc_path], cwd=os.path.dirname(path))
    shutil.rmtree(tmp_arc_path, ignore_errors=True)


if __name__ == '__main__':
    manager.main()
