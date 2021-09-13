#!/bin/sh

#define the template.
cat << "EOF"
#!/bin/sh

MQTT_PASS_PATH="/etc/iotree/.passwd"

while inotifywait -e close_write $MQTT_PASS_PATH; do
   PID="$(pidof mosquitto)"
   kill -SIGHUP $PID
done
EOF
