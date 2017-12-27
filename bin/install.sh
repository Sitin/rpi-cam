#!/usr/bin/env bash -l

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CAPTURE_DIR=${DIR}/../server/rpi_cam/capture

if [ -z "${VIRTUAL_ENV}" ]; then
    echo 'Creating virtual environment...'
    mkvirtualenv --python=`which python3` rpi_cam
    workon rpi_cam
else
    echo 'Already on virtual environment. Skipping virtual environment creation.'
fi

pip install -r ${DIR}/../server/requirements.txt

if [ `uname -m` = 'armv6l' ]; then
    pip install -r ${CAPTURE_DIR}/rpi_capture/requirements.txt
else
    pip install -r ${CAPTURE_DIR}/opencv_capture/requirements.txt
fi
