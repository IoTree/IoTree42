#!/bin/bash
set -e


x=$1
sed -i "48s/.*/    logger.debug('Response headers: %s', response.headers)/" /home/$x/dj_iot/venv2/lib/python3.9/site-packages/revproxy/response.py
sed -i "127s/.*/    logger.debug('Response headers: %s', response.headers)/" /home/$x/dj_iot/venv2/lib/python3.9/site-packages/revproxy/utils.py
