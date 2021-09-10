#!/bin/sh

#listen to mqtt
# This script subscribes to a MQTT topic using mosquitto_sub.
# On each message received, you can execute whatever you want.

while true  # Keep an infinite loop to reconnect when connection lost/broker unavailable
do
    mosquitto_sub -h localhost -p 1883 -t 'sensorbase/SYSTEMcontrolDONOTSAVE/linkgateway' | while read -r payload
    do
        #when incoming read cred. file
        Username=$(sed -n '1p' /etc/giotree/CredentialsFile.txt)
        Password=$(sed -n '2p' /etc/giotree/CredentialsFile.txt)
        GatewayID=$(sed -n '3p' /etc/giotree/CredentialsFile.txt)
        Hostname=$(sed -n '4p' /etc/giotree/CredentialsFile.txt)
        Port=$(sed -n '5p' /etc/giotree/CredentialsFile.txt)
        #save existing config file
        rm -r /etc/mosquitto/mosquitto.conf.link_save
        mv /etc/mosquitto/mosquitto.conf  /etc/mosquitto/mosquitto.conf.link_save
        #write file
        echo 'port 1883' >>/etc/mosquitto/mosquitto.conf
        echo 'allow_anonymous true' >>/etc/mosquitto/mosquitto.conf
        string="connection ${GatewayID}"
        echo ${string} >>/etc/mosquitto/mosquitto.conf
        echo 'cleansession false' >>/etc/mosquitto/mosquitto.conf
        string="address ${Hostname}:${Port}"
        echo ${string} >>/etc/mosquitto/mosquitto.conf
        string="remote_password ${Password}"
        echo ${string} >>/etc/mosquitto/mosquitto.conf
        string="remote_username ${Username}"
        echo ${string} >>/etc/mosquitto/mosquitto.conf
        if [ "$Port" = "8883"]; then
            echo 'bridge_cafile /etc/mosquitto/certs/DST_Root_CA_X3.pem' >>/etc/mosquitto/mosquitto.conf
        fi
        string="remote_clientid ${GatewayID}"
        echo ${string} >>/etc/mosquitto/mosquitto.conf
        string="topic # both 2 sensorbase/ gateways/${Username}/${GatewayID}/"
        echo ${string} >>/etc/mosquitto/mosquitto.conf
        echo >>/etc/mosquitto/mosquitto.conf
        # clean json
        payloadclean=$(tr -d "{}\" " <<< "$payload")
        if [ "$payload" != "{}" ]
        then
            readarray -d , -t arpayload <<< "$payloadclean"
            # loop and add the rest
            for (( n=0; n < ${#arpayload[*]}; n++))
            do
                #split line at :
                readarray -d : -t arline <<< "${arpayload[n]}"
                #check if incoming is same as cred file gateway id -> delete
                if [ "${arline[0]}" != "$GatewayID" ]
                then
                    string="connection ext${arline[0]}"
                    echo ${string} >>/etc/mosquitto/mosquitto.conf
                    echo 'cleansession false' >>/etc/mosquitto/mosquitto.conf
                    echo 'address ${Hostname}:${Port}' >>/etc/mosquitto/mosquitto.conf
                    string="remote_password ${Password}"
                    echo ${string} >>/etc/mosquitto/mosquitto.conf
                    string="remote_username ${Username}"
                    echo ${string} >>/etc/mosquitto/mosquitto.conf
                    if [ "$Port" = "8883"]; then
                        echo 'bridge_cafile /etc/mosquitto/certs/DST_Root_CA_X3.pem' >>/etc/mosquitto/mosquitto.conf
                    fi
                    string="remote_clientid ext${arline[0]}"
                    echo ${string} >>/etc/mosquitto/mosquitto.conf
                    string="topic ${arline[1]} in 2 gateway/${arline[0]}/ gateways/${Username}/${arline[0]}/"
                    echo ${string} >>/etc/mosquitto/mosquitto.conf
                    echo >>/etc/mosquitto/mosquitto.conf
                fi
            done
        fi
        # reload mosquitto
        sudo systemctl restart mosquitto
        sleep 2
        # check if mosquitto is still working
        if pgrep -x "mosquitto" >/dev/null
        then
            # when working send list of gateway id back to server
            # get variables and make json string
            mosquitto_pub -h localhost -p 1883 -t sensorbase/SYSTEMcontrolSAVEJSON/linkgateway -m "$payload"
        else
            # if not get old file again and reload mosquitto
            rm -r /etc/mosquitto/mosquitto.conf
            mv /etc/mosquitto/mosquitto.conf.link_save /etc/mosquitto/mosquitto.conf
            sudo systemctl restart mosquitto
        fi
    done
    sleep 1  # Wait 1 seconds until reconnection
done # &  # Discomment the & to run in background (but you should rather run THIS script in background)
