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
