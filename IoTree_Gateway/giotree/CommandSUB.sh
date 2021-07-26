#!/bin/bash


# This script subscribes to a MQTT topic using mosquitto_sub.
# On each message received, you can execute whatever you want.

while true  # Keep an infinite loop to reconnect when connection lost/broker unavailable
do
    mosquitto_sub -h localhost -p 1883 -t 'sensorbase/SYSTEMcontrolDONOTSAVE/bashCOMMAND' | while read -r payload
    do
        # check for commands and execute them:
        if [ "$payload" == "reboot" ]
        then
            echo "$(sudo reboot)"
        fi

        if [ "$payload" == "update" ]
        then
            echo "$(sudo apt-get update)"
        fi

        if [ "$payload" == "upgrade" ]
        then
            echo "$(sudo apt-get -y upgrade)"
        fi
        # ADD here more commands if needed!
    done
    sleep 1  # Wait 1 seconds until reconnection
done # &  # Discomment the & to run in background (but you should rather run THIS script in background)

