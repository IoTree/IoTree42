#!/bin/sh

#define parameters which are passed in.
USERNAME=$1

#define the template.
cat << EOF
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=$USERNAME
Group=www-data
WorkingDirectory=/home/$USERNAME/dj_iot
ExecStart=/home/$USERNAME/dj_iot/venv2/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          dj_iot.wsgi:application

[Install]
WantedBy=multi-user.target
EOF
