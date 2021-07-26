#!/bin/bash


# This script subscribes to a MQTT topic using mosquitto_sub.
# On each message received, you can execute whatever you want.

while true  # Keep an infinite loop to reconnect when connection lost/broker unavailable
do
    mosquitto_sub -h localhost -p 1883 -t 'sensorbase/SYSTEMcontrolDONOTSAVE/syncfile' | while read -r payload
    do
        # check for commands and execute them:
        echo "$payload" > /etc/giotree/SyncFile.json
    done
    sleep 1  # Wait 1 seconds until reconnection
done # &  # Discomment the & to run in background (but you should rather run THIS script in background)

