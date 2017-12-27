from manager import Manager

import rpi_cam.server

manager = Manager()


@manager.command
def runserver(port=8080):
    """Runs server at <port> (default is 8080)"""
    return rpi_cam.server.run(port=int(port))


if __name__ == '__main__':
    manager.main()
