#!/bin/sh


SYNC_FILE_PATH="/etc/giotree/SyncFile.json"

while inotifywait -e modify $SYNC_FILE_PATH; do
   mosquitto_pub -h localhost -p 1883 -t universe/SYSTEMcontrolSAVEJSON/syncfile -m "$(cat $SYNC_FILE_PATH)"
done
