#!/bin/bash
set -e


x=$1
arch=$(uname -m)
arch2=${arch:0:3}
if [ "$arch2" = "arm" ]; then
echo "architecture: $arch"
sed -i "48s/.*/    logger.debug('Response headers: %s', response.headers)/" /home/$x/dj_iot/venv2/lib/python3.7/site-packages/revproxy/response.py
sed -i "127s/.*/    logger.debug('Response headers: %s', response.headers)/" /home/$x/dj_iot/venv2/lib/python3.7/site-packages/revproxy/utils.py
else
sed -i "48s/.*/    logger.debug('Response headers: %s', response.headers)/" /home/$x/dj_iot/venv2/lib/python3.9/site-packages/revproxy/response.py
sed -i "127s/.*/    logger.debug('Response headers: %s', response.headers)/" /home/$x/dj_iot/venv2/lib/python3.9/site-packages/revproxy/utils.py
fi