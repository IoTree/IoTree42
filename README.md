# IoTree42 
##### OpenSource IoT Platform, Network and Data Warehouse for Privacy-Compliant Applications in Research and Industry

## Installation:

### Requirements: 
The setup and platform has been tested on a cleanly installed Debian server 9/10 and Rpi 3B+ / 4 (recommended).
If TLS (HTTPs) is used, the certificates should be present (tested with let's encrypt authority).
It is recommended to create a new Linux user under which the platform will run.


### Run the setup.sh
For a clean full setup (--full) this includes an SSL certificate setup signed by Let's encrypt Nginx, InfluxDB (v1.8.9), Grafana, Django, Gunicorn, Mosquitto.
If you plan to use your own certificate authority, Jan-Piet Men's CA Generator would be a good place to start. It is included in the repository: https://github.com/IoTree/Performance_Test_Tool.
An installation for local use e.g. on a raspberry type the argument (--raspberry) insted. 
#### NOTE: please setup the certs befor running setup.sh --full.
```
sudo apt-get update 
```
```
sudo apt-get -y upgrade
```

download repository with git:
```
git clone https://github.com/IoTree/IoTree42.git
```

```
cd IoTree42 && sudo bash setup.sh --full 
```
For local use only (no TLS) e.g. on an rasperry Pi:
```
cd IoTree42 && sudo bash setup.sh --raspberry
```

You will be asked for the Linux username and a password to secure your admin access for django.

The installation might take a while...!

### set cron jobs
Finally, it is recommended to set up some cron jobs that start some scripts at boot time.
```
crontab -e
```
At the end add this lines (fill out "<user>").
```
@reboot bash /etc/iotree/reload3.sh
@reboot cd /home/<user>/iot42 && /home/<user>/iot42/env/bin/python /home/<user>/iot42/mqttoinflux6.1.py
```
save, close and reboot.
Your IoTree42 platform is installed and ready for your tasks.
.

## additional installations
### Gateway and server share the same hardware.
You might want to tweck the mosquitto.conf file for your application e.g., change allow anonymus to True.
*******

### In production
You sould uncommend the last part of the settings.py file from django.
However, you can also install a firewall like ufw and fail2ban to increase security.

## Points of failure
Please check after instalation if Gateway ZIP file has a .pem pulic key included.
Also check if DNS in /etc/iotree/config.json is OK, es well as the rest.

## Testing of MQTT-Server/Network performance
Please take a look at the repository: for [python](https://github.com/IoTree/IoTree42/tree/master/API_examples) ****

## Extending IoTree backend.
### A more advanced backend written in Node Red with filters, weather features and more can be fond in the repo. [here](https://github.com/IoTree/IoTree42_Extensions)

## Rest API
### some API examples for python, R and Node-red are found [here](https://github.com/IoTree/Example_API)


## How it works
### General:
##### server: 
The installation includes Eclipse Mosquitto as broker, Django as web framework and Inlfuxdb as database. Optionally, nginx and gunicorn can be installed and configured as web servers.

##### Gateway:
The gateway forwards all incoming messages under the MQTT-Topic "universe/#" to the Platform.
instructions and instaltion files to setup upa gateway are downlaoded from the server once it deployd and running.

##### Devices: 
The devices can be sensors/actuators, APIs of other parties, logging streams, 3D printers and much more.
The data should be sent in a JSON compliant sysntax.

A basic network structure is shown below, it simply shows a branch with a gateway.
![alt text](https://github.com/IoTree/IoTree42/blob/master/.gitignore/in_a_nutshell.png)

The sensor base (e.g. microcontroller..), to which the sensor is connected, sends the respective measured values via mqtt to the gateway.
The gateway itself can be a sensor host.
Then the gateway sends the data (encrypted) to the server, where it is stored in a database.
The data can be looked up on the website or via the RESTful-API.
On the server side, there is essentially Django, Moquitto Broker, a simple Python script that stores all incoming messages to InfluxdB. 
The Gateway can be any Device capable of running mosquitto Broker.


## How to use:
There is no complete documentation, but take a look at the [HowTo](https://github.com/IoTree/IoTree42/blob/master/HowTo.md) and [FAQ](https://github.com/IoTree/IoTree42/blob/master/FAQ.md).
After installing the server, a small manual is also available on the website.


## At last:

There is NO WARRANTY or guarantee FOR LOUSING DATA on both sides, server and gateway.
The operator takes NO RESPON on anything. THE USE of IoTree42 and anything related to it, IS ON YOUR OWN RISK.
