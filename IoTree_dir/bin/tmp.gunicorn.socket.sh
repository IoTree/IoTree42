#!/bin/sh

#define the template.
cat << EOF
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
EOF
