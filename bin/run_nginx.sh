#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SERVER_DIR=${DIR}/../server

nginx -c ${SERVER_DIR}/nginx.conf
