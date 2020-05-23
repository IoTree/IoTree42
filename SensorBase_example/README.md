## DHT22_ESP32 Sensorbase example
### ESP32
#### this code will do:
1. connect to Wi-Fi router
2. collect measurements
- each measurement contain: Temperature, Humidity
3. sends the measurements as json string to the Gateway

for more information refere and thx to:
https://xylem.aegean.gr/~modestos/mo.blog/esp32-send-dht-to-mqtt-and-deepsleep/

please define all necessary parameter in the script such as:
- Gateway IP
- Wifi logins
- Gpio of one wire connection
- type of DHT (22/11)

## DHT22_RPI Sensorbase example
### RPI 2 - 4 /zero
#### this code will do:
1. connect to Wi-Fi router
2. collect measurements
- each measurement contain: Temperature, Humidity, Time
3. sends the measurements as json string to the Gateway

Install python Module "paho.mqtt" and "Adafruit_DHT".

please define all necessary parameter in the script such as:
- Gateway IP
- Gpio of one wire connection
- type of DHT (22/11)

## Lux Sensorbase example
### Adafruit Feather m0 Wi-Fi with tsl2591
#### this code will do:

1. connect to Wi-Fi router
2. collect measurements (how many can be defined)
- each measurement contain: lux with timestamp provided by udp server
3. sends the measurements as json string to the Gateway

if the feather is plug to power chare.

 -> Measurement will stop and send. 
 
if the feather is unplugged form power.

 -> measurement will begin

please define all necessary parameter in the script such as:
- Wi-Fi
- Gateway IP

## Radon Sensorbase example
### Raspberry Zero w with RD200M
#### this code will do:

1. connect to Wi-Fi router
2. collect measurements (how many can be defined)
- each measurement contain: lux with timestamp provided by udp server
3. sends the measurements as json string to the Gateway

if the feather is plug to power chare.

 -> Measurement will stop and send. 
 
if the feather is unplugged form power.

 -> measurement will begin

please define all necessary parameter in the script such as:
- Wi-Fi
- Gateway IP
