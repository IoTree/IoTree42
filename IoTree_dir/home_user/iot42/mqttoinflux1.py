
#!pyton3
import paho.mqtt.client as paho
import datetime
import json
import time
import re
import os
from influxdb import InfluxDBClient

with open('/etc/iotree/config.json', encoding='utf-8') as config_file:
   config = json.load(config_file)

###set variable
mqttbase = "gateways"                   ## Here qu can define the first instance of subscriber of mqtt.
mqttbase2 = mqttbase+"/#"               ## do nothing
broker = "0.0.0.0"                      ## Here you can define the adress of
port = 1883                             ## The adress must match the on in the ssl key.
username = os.environ['MQTT_TODB_NAME']
password = os.environ['MQTT_TODB_PASS']


### mking two lists out of topic sting for later save in db and chacking stings
def buildtree(topic):
    topics = topic.split('/')
    suptopics = topics[2:]
    ## change or deleting all non alnum $$ _ && - characters for later simplification
    suptopicss = [w.replace('_', '-') for w in suptopics]
    suptopicsss = []
    for w in suptopicss:
        suptopicsss.append(re.sub('[^0-9^a-z^A-Z^-]',"", w))
    return topics, suptopicsss

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(mqttbase2)

def on_message(client, userdata, msg):
    message=msg.payload.decode("utf-8")
    message=str(message)
    receiveTime=datetime.datetime.now()
    #print(str(receiveTime) + ": " + msgtopic + " " + message2)
    try:
        tree, suptree=buildtree(msg.topic)
        fluxtopic = '/'.join(map(str, suptree))
        client_flux.switch_database(str(tree[1]))
        tags = {"tag":fluxtopic}
        data = [{"measurement": fluxtopic, "tags": tags, "fields": json.loads(message)}]
        time.sleep(0.05)
        t = client_flux.write_points(data)
        print(t)
    except:
        print("no json")

###setup for influxdb connection###
username_flux = config['MQTTOFLUX_USER']
password_flux = config['MQTTOFLUX_PW']
client_flux =InfluxDBClient(host=config['FLUX_ADRESS'], port=int(config['FLUX_PORT']), username=username_flux, password=password_flux)


###setup for broker connection###
conn_flag=False
client = paho.Client(broker)
client.username_pw_set(username, password)
#client.tls_set(ca)
#client.tls_insecure_set(False)
client.on_connect=on_connect
#client.on_disconnect=on_disconnect
client.on_message=on_message
print("Connecting to broker ", broker)

client.connect(broker,port)

client.loop_forever()


