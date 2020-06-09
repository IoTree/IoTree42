#!/bin/sh

#define parameters which are passed in.
DOMAIN=$1

#define the template.
cat << EOF
per_listener_settings true

listener 1883 localhost

allow_anonymous false

listener 8883

cafile /etc/ssl/certs/DST_Root_CA_X3.pem

certfile /etc/letsencrypt/live/$DOMAIN/fullchain.pem

keyfile /etc/letsencrypt/live/$DOMAIN/privkey.pem


allow_anonymous false

password_file /etc/iotree/.passwd

acl_file /etc/iotree/.acl

pid_file /etc/mosquitto/tmppid

EOF
