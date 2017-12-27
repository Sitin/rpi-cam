#!/usr/bin/env bash -l

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CAPTURE_DIR=${DIR}/../server/rpi_cam/capture

if [ -z "${VIRTUAL_ENV}" ]; then
    echo 'Creating virtual environment...'
    mkvirtualenv --python=`which python3` rpi_cam
else
    echo 'Already on virtual environment. Skipping virtual environment creation.'
fi

source ${HOME}/.profile
workon rpi_cam

echo "Install general requirements"
pip3 install -r ${DIR}/../server/requirements.txt

if [[ "${RPI_CAM_DEV_MODE}" = "True" ]]; then
    echo "Install OpenCV requirements"
    pip3 install -r ${CAPTURE_DIR}/opencv_capture/requirements.txt
else
    echo "Install Paspberry PI requirements"
    pip3 install -r ${CAPTURE_DIR}/rpi_capture/requirements.txt
fi
