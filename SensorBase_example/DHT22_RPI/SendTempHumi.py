#!pyton3


import socket
import time
import paho.mqtt.client as paho
import json
import Adafruit_DHT



# define all variables #
hostname = socket.gethostname()     # hostname for connecting to self
measurement_interval = 20          # in sec
sensor = Adafruit_DHT.DHT22         # set type of DHT sensor
gpio = 4                            # set gpio of one wire connection


def get_cpu_temperature():
    humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio)
    return int(humidity), int(temperature)


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
client = paho.Client('TempHumi')
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
    temp, humi = get_cpu_temperature()
    now = int(time.time())
    payload['Time'] = now
    payload['Temperature'] = temp
    payload['Humidity'] = humi
    payload['Sensor'] = "DHT"
    payloadj = json.dumps(payload)
    topic = "sensorbase/DHT_RPI"
    print(topic, payload)
    client.publish(topic, payloadj)
    print('time: '+str(now)+' Temperature: '+str(temp))
    client.loop_stop()
    time.sleep(measurement_interval)
