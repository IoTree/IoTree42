#!/bin/sh

#define the template.
cat << "EOF"
listener 1883

allow_anonymous false

password_file /etc/iotree/.passwd

acl_file /etc/iotree/.acl

pid_file /etc/mosquitto/tmppid


EOF
