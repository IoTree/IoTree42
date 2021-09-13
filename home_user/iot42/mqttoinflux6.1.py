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
import json
import re
import requests
import multiprocessing

with open('/etc/iotree/config.json', encoding='utf-8') as config_file:
   config = json.load(config_file)

### set variable ###
mqttbase = "gateways"                   ## Here qu can define the first instance of subscriber of mqtt.
mqttbase2 = mqttbase+"/#"               ## do nothing
broker = "0.0.0.0"                      ## Here you can define the adress of
port = 1883                             ## The adress must match the on in the ssl key.
username = config["MQTTUSER"]
password = config["MQTTPASS"]
q=multiprocessing.Queue()
set_threads = 4

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(mqttbase2, qos=0)

def on_message(client,userdata, msg):
    m_decode=str(msg.payload.decode("utf-8","ignore"))
    data={}
    data["topic"]=msg.topic
    data["message"]=m_decode
    if msg.topic.find("DONOTSAVE")<=0:
        q.put(data) #put messages on queue




## main programm part for saving messages on queue to db ###
def log_worker(q):
    while Log_worker_flag:
        while not q.empty():
            results = q.get()
            if results is None:
                continue
#            if True:
            try:
                tree = re.sub('[^0-9^a-z^A-Z/]','', results["topic"]).split('/', 2)[1:]
                payload_list = json.loads(results["message"])
#                print(results["message"])
                data = []
                if not isinstance(payload_list, list):
                    lis = []
                    lis.append(payload_list)
                    payload_list = lis
                for payload_user in payload_list:
                    if not isinstance(payload_user, dict):
                        print("no dict")
                        break
                    data.extend([tree[1], ',tag=', tree[1], ' '])
                    for n in payload_user:
                        if isinstance(payload_user[n], (int, float)):
                            data.extend([n,'=',payload_user[n], ','])
                        else:
                            data.extend([n, '=', '"{}"'.format(payload_user[n]), ','])
                    del data[-1]
                    if "timestamp" in payload_user:   ### checking for timestamp in msg to use it as the db timestamp ###
                        data.extend([' ', int(payload_user["timestamp"]*1000000000)]) ## nano sec ##
                    data.extend(['\n'])
                if data:
                    del data[-1]
                    params_user = params + (('db', tree[0]),)
                    rr = requests.post(adress_flux, params=params_user, data=''.join(map(str, data)))
                else:
                    print("no proper json")
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
    t = multiprocessing.Process(target=log_worker,args=(q,)) #start logger
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

