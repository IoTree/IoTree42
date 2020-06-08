#!pyton3.6

"""
//Iotree42 sensor Network
//purpose: collecting CPU-Temperature and sendig it to Gateway
//used software: python3.6, python paho module
//for hardware: Debian-Server
//design by Sebastian Stadler
//on behalf of the university of munich.
//NO WARRANTY AND NO LIABILITY
//use of the code at your own risk.
//https://github.com/IoTree/IoTree42
"""

import socket
import time
import paho.mqtt.client as paho
import json
import requests


# define all variables #
hostname = socket.gethostname()   # hostname for connecting to self
measurement_interval = 3600       # in sec
api_key = ""                      #api_key form openweathermap.org
url = "http://api.openweathermap.org/data/2.5/weather"
city = ""                         # city 
country = ""                      # country like uk, de, ....

def get_weather_data():
    r = requests.get(url+'?q='+city+','+country+'&appid='+api_key)
    r_dict = json.loads(r.text)
    return r_dict


# def for connecting to self/localhost #
def on_log(client, userdata, level, buf):
    print("log: "+buf)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected OK")
    else:
        print("Bad connection Returned code=", rc)


def on_disconnect(client, userdata, flags, rc=0):
    print("DisConnected result code "+str(rc))


def on_message(client, userdata, msg):
    m_decode = str(msg.payload.decode("utf-8", "ignor"))
    print("message received", m_decode)


# Client for Sensorbases and subgateways
client = paho.Client('cputemp')
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
print("Connecting to broker2 ", hostname)
client.connect(hostname, 1883)

print('Starting measurement and sending')
print('measurement_interval: '+str(measurement_interval))
payload={}

while True:
    client.loop_start()
    time.sleep(1)
    data = get_weather_data()
    now = int(time.time())
    del data["weather"][0]["id"]
    del data["weather"][0]["icon"]
    del data["sys"]["type"]
    del data["sys"]["id"]
    payload.update(data["main"])
    payload.update(data["weather"][0])
    payload.update(data["clouds"])
    payload.update(data["wind"])
    payload.update(data["sys"])
    payload["city"] = (data["name"])
    payload["dt"] = (data["dt"])
    payload['Time'] = now
    payload['Link'] = "https://openweathermap.org"
    payloadj = json.dumps(payload)
    topic = "sensorbase/weather/"+city
    print(topic, payload)
    client.publish(topic, payloadj)
    client.loop_stop()
    time.sleep(measurement_interval)


