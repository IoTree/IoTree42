# IoTree42 
The number of sensors is steadily increasing. We find a huge number of sensors in commercial environments such as fabrication processes, surveillance systems, environmental measurements (e.g. weather data), but also increasingly in smart home ecosystems or wearable devices. For commercial application there is a variety of software solutions to connect all the sensors storing, displaying or monitoring the collected data. 

For personal, educational or scientific purposes or settings, where money is a strictly limited resource, there is a lack of an easy-to-use and robust data warehouse, that respects your data privacy. Most of the popular cloud based IoT platforms (e.g. Thingspeak) are either closed source, limited in the possibility to expand, charging for premium features or do not meet the strict European data privacy laws, when storing sensitive personal data. 
The following project fills this gap by providing an open source software that is capable to scale and collect data from thousands of sensors and make the data accessible easily.
IoTree42 consists of three parts. The server, that stores the data, the gateway, that connects to the server via TLS and the sensor itself. The server runs on any i386 or ARM platform with a Linux operating system. For the gateway you can choose between a low budget ARM or ESP system. The data is sent from the sensor via the widespread Mqtt protocol using a JSON formatted data set. The server receives the data and stores it in a database (MongoDB). Users can access the data via an easy to use multiuser web interface or by using a RESTAPI. 
IoTree42 is an easy to use data warehouse and IoT platform with a lot of possibilities for collecting and distributing sensor data for educational or scientific purposes or even for running it at home.

## How it works
The basic Structure is illustrated below.
![alt text](https://github.com/IoTree/IoTree42/blob/master/.gitignore/in_a_nutshell.png)

The sensor bases to which the sensor is connected send the respectively measured values ??via mqtt to the gateway.
The gateway itself can be a sensor base.
Then the gateway sends the data (encrypted) to the server, where it is stored in a database.
The data can be looked up on the website or via the rest API.
On the server side there are basically Django, Moquitto Broker, a basic Python scrip that stores all incoming messages on the Mongo-dB. Additionally the connection between Gateway and Server can be TLS-encrypted.
On the webpage provided by your Django server is a detailed manual and an installation instruction for the gateway. It also can be found [here](https://github.com/IoTree/IoTree42/blob/master/IoTree_dir/home_user/README.md).
The Gateway can be any Device capable of running mosquitto Broker and Python.

## Installation:
### Requirements: 
Mongo dB version 2.7 or higher must be installed!
It may not work with Resparrian because it is a 32-bit operating system and you will need a 64-bit operating system.
It is possible to install Ubuntu on Raspberry Pi to achieve full 64-bit.
The other way would be to optimize Pymongo to work with Mongo dB version 2.4.

The setup was tested on Debian 9.

```
sudo apt-get update 
```
```
sudo apt-get -y upgrade
```

download repository with git:
```
git clone https://github.com:IoTree/IoTree42.git
```
```
cd IoTree42/IoTree_dir 
```

### setup.sh
Install with sudo bash setup.sh
For a complete setup, this includes an SSL certificate creation provided by Let's encrypt and Nginx as web server do:
```
sudo bash setup.sh --letsencrypt --nginx
```
Without ssl encryption but with nginx do (recommended):
```
sudo bash setup.sh --nginx
```
or:
```
sudo bash setup.sh
```
It is possible to add the encryption later for exaple with Openssl tutorials can be found [here](http://www.steves-internet-guide.com/mosquitto-tls/) and [here](https://mosquitto.org/man/mosquitto-tls-7.html).
You have to change the IoTree_Gateway_V_1.0.zip so that it contains the required certificate (client) for the gateway.


The installation can take a while...

You will be ask for the linux Username. This is needed to save all files in the right directory.

Also you will be asked for an email, a password and an admin-mail.
  The first e-mail and password are for the server to send password resets.
  Not all email providers work, but Gmail usually works. More information can be found [here](https://www.dev2qa.com/how-do-i-enable-less-secure-apps-on-gmail/) and [here](https://support.google.com/a/answer/176600?hl=en).
  The administrator email is for the user and server to send problems and information to you.

### set crontab jobs
we need to set up a crontab job so user will be register on mosquitto broker.
```
sudo crontab -e
```
At the end add these two lines.
```
@reboot bash /etc/iotree/reload3.sh
@reboot bash /etc/iotree/hash3.sh
```
save and close it.

### Installations of python modules and test.
```
cd ~./iot42 
```
install all the requirements.

```
virtualenv -p python3 venv1
source venv1/bin/activate
pip3 install -r requrements.txt
```
do the same for the Django requirements.
```
cd ~./dj_iot
```
you can choose with virtual environment:
```
virtualenv -p python3 venv2
source venv2/bin/activate
pip3 install -r requirements.txt
```

### Setup Django
you will need to make a superuser.
```
source venv2/bin/activate
python3 manage.py createsuperuser
```
with this user you can enter the admin-page under "<your site name or ip>/admin"
also migrate to be sure all implementation are set:
```
python3 manage.py makemigrations
python3 manage.py migrate
```
Collect all static files.
```
python3 manage.py collectstatic
```

now Django is setup and you can test it.
```
python3 manage.py runserver <your ip:8000>
```
go in your browser to (your ip):8000

## Run it all
To execute it all:
```
cd ~./iot42
```
start the mqttodb1.py in the background without nohup.out:
```
source venv1/bin/activate
nohup python3 mqttoinflux1.py </dev/null >/dev/null 2>&1 &
```
Now start the django server without nginx:
```
cd ~./dj_iot
```
```
source venv2/bin/activate
python3 manage.py runserver <your dns or ip:8000>
```
OR start the django server with nginx:
```
sudo systemctl restart nginx
sudo systemctl restart gunicorn
```

## additional installations
### Gateway and server share the same hardware.
install without let's encrypt..
Then you can just download and install the gateway repository. Explant on the Setup Gateway page.
If you also want to use SSL encryption, you must customize the gateway script mqttbgidge1.py to meet your needs.
Look at mqttodb1.py as an example.

### Deploy on a real server.
It is recommended to do everything on an Apache server.
A possible Apache2 configuration file can be found [here](https://github.com/IoTree/IoTree42/blob/master/apache_conf_example).
You may also want to install a firewall like ufw for security.
and if you have a DNS name, lets encrypt would be a good choice.

## Rest API
### some API examples are found here:
for [python](https://github.com/IoTree/IoTree42/tree/master/API_examples)
for [R](https://github.com/IoTree/IoTree42/tree/master/API_examples)

## At last:

There is NO WARRANTY or guarantee FOR LOUSING DATA on both sides, server and gateway.
The operator takes NO RESPON on anything. THE USE of IoTree42 and anything related to it, IS ON YOUR OWN RISK.


### Found some bugs?
Contact me

