#!python3

# mqtt module importieren
import paho.mqtt.client as mqtt

# Adafruit Bibliothek importieren
import Adafruit_DHT

#Config
sensor = Adafruit_DHT.DHT22      # module has to be installed
gpio = 4                         #one wire connection to gpio:? default: 4
broker = ""                      #ip of broker like 192.168.188.[...]



#import
import paho.mqtt.client as paho
import json
import time



port = 1883                             ## The adress must match the on in the ssl key.


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
#    client.subscribe(mqttbase2)
    while True:
        print("@ While loop")
        # Daten auslesen
        timenow = time.time()
        humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio)
        dictdata = {'Temperature': temperature, 'Humidity':humidity, 'Time': timenow}
        data=json.dumps(dictdata)
        client.publish("sensorbases/DHT22", data)
        print (data)
        time.sleep(60)


def on_message(client, userdata, msg):
    message=msg.payload.decode("utf-8")


###setup for broker connection###
conn_flag=False
client = paho.Client(broker)
client.on_connect=on_connect
client.on_message=on_message
print("Connecting to broker ", broker)

client.connect(broker,port)

client.loop_forever()
