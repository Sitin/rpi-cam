from manager import Manager

import rpi_cam.server

manager = Manager()


@manager.command
def runserver(port=8080, path='/tmp/rpi_cam.sock', host=None):
    """Runs server at <port> (default is 8080)"""
    return rpi_cam.server.run(port=int(port), path=path, host=host)


if __name__ == '__main__':
    manager.main()
