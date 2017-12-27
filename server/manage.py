from manager import Manager

import rpi_cam.server
from rpi_cam.capture import Drivers

manager = Manager()


@manager.command
def runserver(port=8080, path='/tmp/rpi_cam.sock', host=None, driver=Drivers.RPI):
    """Runs server at <port> (default is 8080)"""
    return rpi_cam.server.run(port=int(port), path=path, host=host, driver=driver)


if __name__ == '__main__':
    manager.main()
