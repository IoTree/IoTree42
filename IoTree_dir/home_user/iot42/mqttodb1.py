#!/usr/bin/env python3.6

"""
//Iotree42 sensor Network

//purpose: saving incoming data from gateway to mongodb
//used software: python3, python paho module, pymongo
//for hardware: Debian-Server

//design by Sebastian Stadler
//on behalf of the university of munich.

//NO WARRANTY AND NO LIABILITY
//use of the code at your own risk.
"""

import paho.mqtt.client as paho
import datetime
from pymongo import MongoClient
import json
import re
import os

with open('/etc/iotree/config.json', encoding='utf-8') as config_file:
   config = json.load(config_file)


# set variable #
mqttbase = "gateways" # Here qu can define the first instance of subscriber of mqtt.
mqttbase2 = mqttbase+"/#"  # do nothing
broker = "0.0.0.0"
port = 1883
username = config.get('MQTT_TODB_NAME')  # mosquitto-Broker user credentials
password = config.get('MQTT_TODB_PASS')


def buildtree(topic):  # making two lists out of string topic, for checking and saving
    topics = topic.split('/')
    suptopics = topics[3:]
    suptopicss = [w.replace('_', '-') for w in suptopics]  # change "_" to "-"
    suptopicsss = []
    for w in suptopicss:  # allow only alphanumeric and "-" characters for later simplification
        suptopicsss.append(re.sub('[^0-9^a-z^A-Z^-]',"", w))
    return topics, suptopicsss

def on_connect(client, userdata, flags, rc):  # func. to connect to mosquitto-Broker/Server
    print("Connected with result code "+str(rc))
    client.subscribe(mqttbase2, qos=2)  # subscribe to topic define before with quality of service = 2

def on_message(client, userdata, msg):  # func. for handling incoming massage and post process
    receiveTime=datetime.datetime.now()
    message=msg.payload.decode("utf-8")
    message=str(message)
    print(str(receiveTime) + ": " + msg.topic + " " + message)
    try:
        message2=json.loads(message)
        tree, suptree=buildtree(msg.topic)
        post={"data":message2}
        collection.update({"owner":tree[1], "gateways_id":tree[2], "tree":suptree},{"$set":{"owner":tree[1], "gateways_id":tree[2], "tree":suptree}},upsert=True)
        collection.update({"owner":tree[1], "gateways_id":tree[2], "tree":suptree}, {'$push':post})
    except:
        print("no json")


# setup for mongodb connection #
mongoClient = MongoClient(config.get('MANGO_ADRESS'))
db = mongoClient[config.get('MANGO_DATABASE')]
collection = db[config.get('MANGO_DATA_COL')]


# setup for broker connection #
conn_flag=False
client = paho.Client(broker)
client.username_pw_set(username, password)
client.on_connect=on_connect
#client.on_disconnect=on_disconnect
client.on_message=on_message
print("Connecting to broker ", broker)

# start connection #
client.connect(broker,port)

client.loop_forever()

