"""
//Iotree42 sensor Network

//purpose: connecting django to pymongo to mongodb, also for checking data and process data for later use
//used software: python3, python module pymongo, json, time, re
//for hardware: Debian-Server

//design by Sebastian Stadler
//on behalf of the university of munich.

//NO WARRANTY AND NO LIABILITY
//use of the code at your own risk.
"""

import paho.mqtt.client as mqtt
import json

with open('/etc/iotree/config.json', encoding='utf-8') as config_file:
   config = json.load(config_file)


class PahoSend:
    def __init__(self, username, gateway, topic):
        self.user=username
        self.gateway=gateway
        self.topic=topic
        self.broker_address="0.0.0.0"
        self.broker_port=1883

    def checkjson(self, message):
        try:
            jsondic = json.loads(message)
        except ValueError as err:
            return False
        return json.dumps(jsondic)

    def send(self, message):
        try:
            client = mqtt.Client("mqttodb"+self.user)
            client.username_pw_set(config["MQTTUSER"], config["MQTTPASS"])
            client.connect(self.broker_address, self.broker_port)
            topic = "gateways/"+self.user+"/"+self.gateway+"/"+self.topic
            #print (topic)
            client.loop_start()
            r = client.publish(topic, message, qos=2)
            print (r)
            client.loop_stop()
            client.disconnect()
            return True
        except Exception:
            return False

