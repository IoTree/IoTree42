#!/bin/sh

#define parameters which are passed in.
DOMAIN=$1

#define the template.
cat << EOF
port 8883

cafile /etc/ssl/certs/DST_Root_CA_X3.pem

certfile /etc/letsencrypt/live/$DOMAIN/fullchain.pem

keyfile /etc/letsencrypt/live/$DOMAIN/privkey.pem


allow_anonymous false

password_file /etc/iotree/.passwd

acl_file /etc/iotree/.acl

pid_file /etc/mosquitto/tmppid

listener 1883 0.0.0.0
EOF
