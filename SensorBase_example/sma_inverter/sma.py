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
from pymodbus.client.sync import ModbusTcpClient as ModbusClient


# define all variables #
hostname = socket.gethostname()     # hostname for connecting to self, change if Gateway is not the same device 
measurement_interval = 20           # in sec
sma_inverter_ip = ""                # enter the ip of the sma_inverter as string
sma_modbus_port = 502               # enter the port of the modbus tcp normaly 502. Also make shure to enable the modbus tcp in your inverter



def get_w_sma():
    rr = client_sma.read_holding_registers(30775, 10, unit=3)
    return rr

def get_w_sma_day():
    rr = client_sma.read_holding_registers(30517, 4, unit=3)
    return rr.registers[3]


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
client = paho.Client('sma_inverter')
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
print("Connecting to broker2 ", hostname)
client.connect(hostname, 1883)
print('Starting measurement and sending')
print('measurement_interval: '+str(measurement_interval))
payload={}

while True:
    try:
        client.loop_start()
        client_sma = ModbusClient(sma_inverter_ip, port=sma_modbus_port)
        time.sleep(1)
        sma_watt_all = get_w_sma()
        sma_watt_sum = sma_watt_all.registers[1]
        sma_watth_day = get_w_sma_day()
        now = int(time.time())
        client_sma.close()
        payload['Time'] = now
        payload['SMA_Watt_sum'] = sma_watt_sum
        payload['SMA_Watth_day'] = sma_watth_day
        payload['SMA_Watt_channel_1'] = sma_watt_all.registers[3]
        payload['SMA_Watt_channel_2'] = sma_watt_all.registers[5]
        payload['SMA_Watt_channel_3'] = sma_watt_all.registers[7]
        payload['Sensor'] = "modbus PV Sunny Tripower 5.0"
        payloadj = json.dumps(payload)
        topic = "sensorbase/sma_pv/sma_watt"
        print(topic, payload)
        client.publish(topic, payloadj)
        print('time: '+str(now)+' SMA_Watt: '+str(sma_watt_sum))
        client.loop_stop()
        time.sleep(measurement_interval)
    except Exception:
        client_sma.close()
        del client_sma
        client.loop_stop()
        print("some error")
        time.sleep(measurement_interval)
        continue


