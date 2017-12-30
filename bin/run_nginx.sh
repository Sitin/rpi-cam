#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SERVER_DIR=${DIR}/../server
TMP_DIR=/tmp/rpi_cam/

# Create temporary directories
mkdir -p ${TMP_DIR}
mkdir -p ${TMP_DIR}/pids
mkdir -p ${TMP_DIR}/www

# Create a symlink to cam_data/ directory
rm -f ${TMP_DIR}/www/cam_data
ln -s ${SERVER_DIR}/cam_data ${TMP_DIR}/www/cam_data

nginx -c ${SERVER_DIR}/nginx.conf
