#!/bin/bash


echo "******************************************"
echo "*  _____   _______            _  _ ___   *"
echo "* |_   _| |__   __|          | || |__ \  *"
echo "*   | |  ___ | |_ __ ___  ___| || |_ ) | *"
echo "*   | | / _ \| | '__/ _ \/ _ \__   _/ /  *"
echo "*  _| || (_) | | | |  __/  __/  | |/ /_  *"
echo "* |_____\___/|_|_|  \___|\___|  |_|____| *"
echo "*                                        *"
echo "******************************************"
echo "<<<-----          Username           --->>>"
echo "ENTER your MQTT-Username is the same as on the Web-Site"
read Username
echo "<<<-----      Broker IP/Hostname     --->>>"
echo "ENTER MQTT-Broker IP or Hostname"
read Hostname
echo "<<<-----         Broker Port         --->>>"
echo "ENTER MQTT-Broker Port normaly 1883 or 8883 for TLS"
read Port
echo "<<<--          MQTT-Password          -->>>"
echo "ENTER your MQTT-Password given to you when registering. !HIDDEN INPUT!"
read -s Password

NEW_UUID=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)

echo 'port 1883' >>./mosquitto.conf
string="connection ${Username}"
echo ${string} >>./mosquitto.conf
string="address ${Hostname}:${Port}"
echo ${string} >>./mosquitto.conf
string="remote_username ${Username}"
echo ${string} >>./mosquitto.conf
echo 'bridge_cafile /etc/mosquitto/certs/DST_Root_CA_X3.pem' >>./mosquitto.conf
string="remote_clientid ${Username}"
echo ${string} >>./mosquitto.conf
string="topic # both 2 sensorbase/ gateways/${Username}/${NEW_UUID}/"
echo ${string} >>./mosquitto.conf

chmod -R 644 ./mosquitto.conf


cp /etc/mosquitto/mosquitto.conf /etc/mosquitto/mosquitto.conf.iotree_save
cp -r ./mosquitto.conf /etc/mosquitto/mosquitto.conf
cp -r ./DST_Root_CA_X3.pem /etc/mosquitto/certs/DST_Root_CA_X3.pem
