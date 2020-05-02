#!/bin/sh

#define the template.
cat << "EOF"
#!/bin/sh

MQTT_PASS_PATH="/etc/iotree/.passwd"
MQTT_HASH_PATH="/etc/iotree/.hashing"

while inotifywait -e close_write $MQTT_HASH_PATH; do
   if [ -s $MQTT_HASH_PATH ]
   then
      mosquitto_passwd -U $MQTT_HASH_PATH
      cat $MQTT_HASH_PATH >> $MQTT_PASS_PATH
      > $MQTT_HASH_PATH
   else
      echo ""
   fi
done
EOF
