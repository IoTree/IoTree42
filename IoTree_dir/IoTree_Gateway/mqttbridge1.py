#!pyton3

"""
github IoTree/IoTree42
"""

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

nossl=False
server_ip = str(config['SERVER_IP'])	  # set server ip
server_port = int(config['SERVER_PORT'])  # set server port
if config['CA_PATH'] == "":
    nossl=True
if not nossl:
   ca_path = config['CA_PATH']		  # set ca.crt path
   cert_path = config['CERT_PATH']		  # set client.crt path
   key_path = config['KEY_PATH']		  # set client.key path
mqtt_username = config['MQTT_USERNAME']	  # set Mqtt Username is given on registration process on www.xyt.com
mqtt_password = config['MQTT_PASSWORD']	  # set Mqtt Password is given on registration process on www.xyt.com


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
	print("DisConnected result code "+str(rc))


def on_message(client, userdata, msg):
	m_decode=str(msg.payload.decode("utf-8","ignor"))
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
	print("DisConnected result code "+str(rc))


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
	client.publish(topic3, m_decode)
	print("message received", m_decode)


# if not define take cpu-serial-number as gateway id #
if not ID:
	ID = getserial()
	print(ID)


# Client connection for sending data to server #
conn_flag = False
client = paho.Client(mqtt_username)
client.username_pw_set(mqtt_username, mqtt_password)
if not nossl:
    client.tls_set(ca_certs=ca_path, certfile=cert_path, keyfile=key_path)
    client.tls_insecure_set(False)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
print("Connecting to broker1 ", server_ip)
client.connect(server_ip, server_port)


# Client for Sensorbases and subgateways
client2 = paho.Client(hostname)
client2.on_connect = on_connect2
client2.on_disconnect = on_disconnect2
client2.on_message = on_message2
print("Connecting to broker2 ", hostname)
client2.connect(hostname, 1883)
client2.subscribe("sensorbase/#")

client2.loop_start()
client.loop_forever()
