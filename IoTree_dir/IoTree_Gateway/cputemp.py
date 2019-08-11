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


# define all variables #
hostname = socket.gethostname()     # hostname for connecting to self
measurement_interval = 20          # in sec


def get_cpu_temperature():
    temp_file = open("/sys/class/thermal/thermal_zone0/temp")
    cpu_temp = temp_file.read()
    temp_file.close()
    return float(cpu_temp)/1000


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
    temp = get_cpu_temperature()
    now = int(time.time())
    payload['Time'] = now
    payload['Temperature'] = temp
    payload['Sensor'] = "Cpu-Temp-Sensor"
    payloadj = json.dumps(payload)
    topic = "sensorbase/getewayself/cputemp"
    print(topic, payload)
    client.publish(topic, payloadj)
    print('time: '+str(now)+' Cpu-Temperature: '+str(temp))
    client.loop_stop()
    time.sleep(measurement_interval)
