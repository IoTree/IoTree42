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
echo "<<<-----   Send Cpu Temperature   ----->>>"
echo "This script sends every 20 sec the Temp."
echo "The message will be published under topic"
echo "sensorbase/getewayself/cputemp"

while true
do
cputemp=$(cat /sys/class/thermal/thermal_zone0/temp)
cputemp=$((cputemp / 1000))
timestamp=$(date "+%s")
echo '{"cputemp":'$cputemp',"timestamp":'$timestamp'}'
mosquitto_pub -h localhost -p 1883 -t sensorbase/gatewayself/cputemp -m '{"cputemp":'$cputemp',"timestamp":'$timestamp'}'
sleep 20
done
