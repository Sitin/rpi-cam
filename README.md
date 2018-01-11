rpi-cam
=======

Raspberry Pi Camera Application

Installation
------------

We strongly suggest to use virtual environment:

```sh
mkvirtualenv --python=`which python3` rpi_cam
workon rpi_cam
```

### Installing general server dependencies

To installing general requirements:

```sh
pip3 install -r server/requirements.txt
```

### Installing Raspberry Pi Python dependencies

Then you should install Raspberry Pi packages (doesn't work on on non-RPi systems):

```sh
pip3 install -r server/rpi_cam/capture/rpi_capture/requirements.txt
```

In order to use Pillow you have to install the following dependencies:

```sh
sudo apt-get install libopenjp2-7 libopenjp2-7-dev
sudo apt-get install libtiff5
```

To use `nginx` you also have to:

```sh
sudo apt-get install nginx
``` 

### Installing alternative (non-RPi) camera drive dependencies

For development on non-raspberry environments we have OpenCV camera driver (too hard and slow on RPi's):

```sh
pip3 install -r server/rpi_cam/capture/opencv_capture/requirements.txt
```

### Installing and building client

First install NPM dependencies:

```sh
cd client/rpi-cam-web
npm install
```

Then to build client application run (under `client/rpi-cam-web`):

```sh
pm run-script build
```

Running
-------

### Running camera server

To run camera server:

```sh
server/manage.py runserver
```

For non-raspberry environments:

```sh
server/manage.py runserver --driver=opencv
```

### Running nginx proxy

You can run optional nginx proxy that speeds up static.

First you need to create nginx config from template:

```sh
server/manage.py nginx_conf
```

And then start the server:

```sh
server/manage.py nginx
```

### Running via [Supervisor](http://supervisord.org/)

First of all, you should install Supervisor:

```sh
sudo apt-get install supervisor
```

Then create configuration file:

```sh
server/manage.py supervisor_conf
```

Copy it into Supervisor configuration directory:

```sh
sudo cp server/rpi_cam-supervisor.conf /etc/supervisor/conf.d/rpi_cam-supervisor.conf
```

And restart the service:

```sh
sudo service supervisor restart
```
