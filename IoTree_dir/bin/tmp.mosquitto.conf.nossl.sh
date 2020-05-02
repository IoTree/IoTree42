#!/bin/sh

#define the template.
cat << "EOF"
port 1883

allow_anonymous false

password_file /etc/iotree/.passwd

acl_file /etc/iotree/.acl

pid_file /etc/mosquitto/tmppid

listener 1883 0.0.0.0
EOF
