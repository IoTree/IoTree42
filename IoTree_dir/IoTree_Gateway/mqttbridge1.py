#!pyton3.6

"""
//Iotree42 sensor Network
//purpose: sending incoming Massages to Server
//used software: python3.6, python paho module
//for hardware: Debian-Server
//design by Sebastian Stadler
//on behalf of the university of munich.
//NO WARRANTY AND NO LIABILITY
//use of the code at your own risk.
//https://github.com/IoTree/IoTree42
"""

import string
import random
import socket
import json
import paho.mqtt.client as paho
import os

# open config file #
with open('.config.json', encoding='utf-8') as config_file:
	config = json.load(config_file)

# define all necessary variables #
ID = ""					# gateway_id, default = cpu-serial-number, can be changed if so
hostname = socket.gethostname()		# get hostname for connecting to localhost and testing

client_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12)) # make a random client_id
			# If you want to continue with a session, you must use a fixed client_id.

nossl=False
server_ip = str(config['SERVER_IP'])	  # set server ip
server_port = int(config['SERVER_PORT'])  # set server port
if config['CA_PATH'] == "":
    nossl=True
if not nossl:
   ca_path = config['CA_PATH']		  # set ca.crt path
#   cert_path = config['CERT_PATH']		  # set client.crt path, no need for this
#   key_path = config['KEY_PATH']		  # set client.key path, no need for this
mqtt_username = config['MQTT_USERNAME']	  # set Mqtt Username is given on registration process on www.your host.com
mqtt_password = config['MQTT_PASSWORD']	  # set Mqtt Password is given on registration process on www.your host.com
mqtt_topics = config['MQTT_SUB_SERVER']   # set the Mqtt sub form server to make conaction bidirectional, in config file make a list of topics.
					  # the massage form server will be puplished under "fromserver/..." 

def getserial():
	# Extract serial from cpuinfo file
	cpuserial = "0000000000000000"
	try:
		f = open('/proc/cpuinfo', 'r')
		for line in f:
			if line[0:6] == 'Serial':
				cpuserial = line[10:26]
		f.close()
	except FileExistsError:
		cpuserial = "ERROR000000000"
	return cpuserial


# def for connecting to server #
def on_log(client, userdata, level, buf):
	print("log: "+buf)


def on_connect(client, userdata, flags, rc):
	if rc == 0:
		print("connected OK")
	else:
		print("Bad connection Returned code=", rc)


def on_disconnect(client, userdata, flags, rc=0):
	print("Server DisConnected result code "+str(rc))


def on_message(client, userdata, msg):
	topic = msg.topic
	m_decode=str(msg.payload.decode("utf-8","ignor"))
	topic1, topic2, topic3, topic4 = topic.split('/', 3)
        topic4 = "fromserver/" + topic4
	client2.publish(topic4, qos=2, payload=m_decode)
	print("message received", m_decode)


# def for connecting to self/localhost #
def on_log2(client2, userdata, level, buf):
	print("log: "+buf)


def on_connect2(client2, userdata, flags, rc):
	if rc == 0:
		print("connected OK")
	else:
		print("Bad connection Returned code=",rc)


def on_disconnect2(client2, userdata, flags, rc=0):
	print("Gateway DisConnected result code "+str(rc))


def on_message2(client2, userdata, msg):
	topic = msg.topic
	m_decode = str(msg.payload.decode("utf-8", "ignor"))
	topic1, topic2 = topic.split('/', 1)
	topic3 = "gateways/"
	topic3 += str(mqtt_username)
	topic3 += "/"
	topic3 += ID
	topic3 += "/"
	topic3 += topic2
	print(topic3)
	client.publish(topic3, qos=2, payload=m_decode)
	print("message received", m_decode)


# if not define take cpu-serial-number as gateway id #
if not ID:
	ID = getserial()
	print(ID)


# Client connection for sending data to server #
conn_flag = False
client = paho.Client(client_id)
client.username_pw_set(mqtt_username, mqtt_password)
if not nossl:
    client.tls_set(ca_certs=ca_path)
    client.tls_insecure_set(False)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
print("Connecting to broker1 ", server_ip)
client.connect(server_ip, server_port)
for topicc in mqtt_topics:
    topicc = "gateways/" + mqtt_username + "/" + ID + topicc
    client.subscribe(topicc)


# Client for Sensorbases and subgateways
client2 = paho.Client(hostname)
client2.on_connect = on_connect2
client2.on_disconnect = on_disconnect2
client2.on_message = on_message2
print("Connecting to broker2 ", hostname)
client2.connect(hostname, 1883)
client2.subscribe("sensorbase/#", qos=2)

client2.loop_start()
client.loop_forever()
