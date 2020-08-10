#!^pyton3

"""
//Iotree42 sensor Network
//purpose: saving mqtt to db
//used software: python3,
//for hardware: Debian-Server, RPI ...
//design by Sebastian Stadler
//on behalf of the university of munich.
//NO WARRANTY AND NO LIABILITY
//use of the code at your own risk.
"""


import paho.mqtt.client as paho
import datetime
import json
import time
import re
import os
import requests
import threading
from queue import Queue

with open('/etc/iotree/config.json', encoding='utf-8') as config_file:
   config = json.load(config_file)

### set variable ###
mqttbase = "gateways"                   ## Here qu can define the first instance of subscriber of mqtt.
mqttbase2 = mqttbase+"/#"               ## do nothing
broker = "0.0.0.0"                      ## Here you can define the adress of
port = 1883                             ## The adress must match the on in the ssl key.
username = config["MQTTUSER"]
password = config["MQTTPASS"]
q=Queue()
set_threads = 3

### mking two lists out of topic sting for later save in db and chacking stings ###
def buildtree(topic):
    topics = topic.split('/')
    suptopics = topics[2:]
    ## change or deleting all non alnum $$ _ && - characters for later simplification
    suptopicss = [w.replace('_', '') for w in suptopics]
    suptopicsss = []
    for w in suptopicss:
        suptopicsss.append(re.sub('[^0-9^a-z^A-Z]',"", w))
    return topics, suptopicsss

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(mqttbase2)

def on_message(client,userdata, msg):
    topic=msg.topic
    m_decode=str(msg.payload.decode("utf-8","ignore"))
    message_handler(client,m_decode,topic)

##put messages on queue ###
def message_handler(client,msg,topic):
    data=dict()
    tnow=time.localtime(time.time())
    m=time.asctime(tnow)+" "+topic+" "+msg
    data["time"]=tnow
    data["topic"]=topic
    data["message"]=msg
    q.put(data) #put messages on queue

## main programm part for saving messages on queue to db ###
def log_worker():
    while Log_worker_flag:
        while not q.empty():
            results = q.get()
            if results is None:
                continue
            try:
                tree, suptree=buildtree(results["topic"])
                fluxtopic = '/'.join(map(str, suptree))
                tags = {"tag":fluxtopic}
                payload_user = json.loads(results["message"])
                data2 = fluxtopic+",tag="+fluxtopic
                data3 = []
                if "timestamp" in payload_user:   ### checking for timestamp in msg to use it as the db timestamp ###
                    for n in payload_user:
                        if isinstance(payload_user[n], int):
                            data3.append(n+'={}'.format(str(payload_user[n])))
                        elif isinstance(payload_user[n], float):
                            data3.append(n+'={}'.format(str(payload_user[n])))
                        else:
                            data3.append(n+'="{}"'.format(str(payload_user[n])))
                    data3 = ','.join(data3)
                    data4 = data2+" "+data3+" "+str(int(payload_user["timestamp"]*1000000000)) ## nano sec ##
                else:
                    for n in payload_user:
                        if isinstance(payload_user[n], int):
                            data3.append(n+'={}'.format(str(payload_user[n])))
                        elif isinstance(payload_user[n], float):
                            data3.append(n+'={}'.format(str(payload_user[n])))
                        else:
                            data3.append(n+'="{}"'.format(str(payload_user[n])))
                    data3 = ','.join(data3)
                    data4 = data2+" "+data3
#                print(data4)
                params_user = params + (('db', str(tree[1])),)
                rr = requests.post(adress_flux, params=params_user, data=data4)
            except Exception:
                print("no json")

###setup for influxdb connection###
host_flux=config['FLUX_ADRESS']
port_flux=int(config['FLUX_PORT'])
adress_flux = "http://"+host_flux+":"+str(port_flux)+"/write"
params = (
    ('p', config['MQTTOFLUX_PW']),
    ('u', config['MQTTOFLUX_USER']),)


### setup for threading ### 
Log_worker_flag=True
threads = []
for i in range(set_threads):
    t = threading.Thread(target=log_worker) #start logger
    threads.append(t)
    t.start() #start logging thread

###setup for broker connection###
conn_flag=False
client = paho.Client(broker)
client.username_pw_set(username, password)
client.on_connect=on_connect
client.on_message=on_message
print("Connecting to broker ", broker)

client.connect(broker,port)

client.loop_forever()

