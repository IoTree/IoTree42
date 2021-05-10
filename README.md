# IoTree42 
The number of sensors is steadily increasing. We find a huge number of sensors in commercial environments such as fabrication processes, surveillance systems, environmental measurements (e.g. weather data), but also increasingly in smart home ecosystems or wearable devices. For commercial application there is a variety of software solutions to connect all the sensors storing, displaying or monitoring the collected data. 

For personal, educational or scientific purposes or settings, where money is a strictly limited resource, there is a lack of an easy-to-use and robust data warehouse, that respects your data privacy. Most of the popular cloud based IoT platforms (e.g. Thingspeak) are either closed source, limited in the possibility to expand, charging for premium features or do not meet the strict European data privacy laws, when storing sensitive personal data. 
The following project fills this gap by providing an open source software that is capable to scale and collect data from thousands of sensors and make the data accessible easily.
IoTree42 consists of three parts. The server, that stores the data, the gateway, that connects to the server via TLS and the sensor itself. The server runs on any i386 or ARM platform with a Linux operating system. For the gateway you can choose between a low budget ARM or ESP system. The data is sent from the sensor via the widespread Mqtt protocol using a JSON formatted data set. The server receives the data and stores it in a database (MongoDB). Users can access the data via an easy to use multiuser web interface or by using a RESTAPI. 
IoTree42 is an easy to use data warehouse and IoT platform with a lot of possibilities for collecting and distributing sensor data for educational or scientific purposes or even 
for running it at home.

## How it works
The basic Structure is illustrated below.
![alt text](https://github.com/IoTree/IoTree42/blob/master/.gitignore/in_a_nutshell.png)

The sensor bases to which the sensor is connected send the respectively measured values ??via mqtt to the gateway.
The gateway itself can be a sensor base.
Then the gateway sends the data (encrypted) to the server, where it is stored in a database.
The data can be looked up on the website or via the rest API.
On the server side there are basically Django, Moquitto Broker, a basic Python scrip that stores all incoming messages on the Mongo-dB. Additionally the connection between Gateway and Server can be TLS-encrypted.
The Gateway can be any Device capable of running mosquitto Broker.


## How to use:
How to use IoTree42 Platform when installed!

### Setup gateway.

For this look at Setting up my RPi.
You will need to know your IP of the gateway or its hostname.
NOTE: Sometimes hostname won’t work. It depends on the DHCP-Server in this network
If everything is running and gateway is displaying 1 times “Connection OK” with status"0",
it should work and your data will reach the server.
As mentioned in Setting up my RPi you can use the python script cputemp.py for testing.

Be sure your Raspberry Pi is up to date and secure with a proper password!
You must define the IP and the port of the gateway on your sensors and actuators as the broker, for the sensors/actuators to work

### Important rules for the PAYLOAD:
  -	It must be in proper JSON-format. If not so it won’t be stored.
  -	Timestamps must be in UNIX-Format. Also the field key needs to be “Time”. This is necessary for the server to recognise this field as a timestamp.
  -	You should use global time UTC +-0.
  -	Don’t use nested objects or Arrays!!!
  -	Do not send multiple JSON strings at once. Send them individually.
  -	Max time increment is 1 millisecond.
  -	Send measurement values as integer not as string.
  
Example payload: {“sensor”: ”tsl2591”, “lux”: 2314, “time”: 1561373832.000}

### Important rules for the TOPIC:
  -	For simplicity only alphanumeric is allowed. If not, wrong characters will be deleted.
  -	Choose your topic and subtopic-levels wisely. So that you can find data later easily.
  -	Always use "sensorbase/" before the sub-topic. Otherwise it will not be processed through the gateway.
  
Example topic: sensorbase/luxsensor/tls2591

### Visualize or to check the incoming data

#### Your IoTree:
  Click on “Your IoTree”.
  ![alt text](https://github.com/IoTree/IoTree42/blob/master/.gitignore/query_data2.png)
  1.	The tree structure corresponds to the MQTT topic defined in your sensorbase and gateway.
      Simply mark the Sensors or the top level nodes you like to work with.
  2.  Set the start and end point.
  3.	Select if you want to download a CSV file or view a spreadsheet or to delete the selected data.
  
### Dashboard with Grafana
Please visied this sites/video to get a overview on how to work with grafana.

https://docs.bitnami.com/virtual-machine/infrastructure/grafana/get-started/get-started/

  
### Rest API
You will need a REST-API Auth Tocken first
Send a POST request to "<server address>/api-token-auth/"
Containing your login credentials.
You will receive an auth-Token.
  
Example: 

  curl --header "Content-Type: application/json" --request POST --data '{"username":"xyz","password":"xyz"}' https://-server address-/api-token-auth/

Then you connect your applications with Rest-Api trough the link "-server ad.-/iotree_api".

If sending a GET request the server will answer with all the nodes and leaves you have.

Then you can do your queries:
#### The json string is declared as follows:
  {
  "tree": "Choice one or several of your leeds by ID",
  "time_start": "start of interval in milliseconds",
  "time_end": "End of interval in milliseconds"
  }.
  
#### example of a POST can look like this:
  {"tree": {"gateway1/gatewayself/cputemp"}, "time_start":"0", "time_end":"1559187967000"}
  
#### Or like this:
  {"tree": {"gateway1/gatewayself/cputemp", "LUXSensor/tls2591"}, "time_start":"1559187967000", "time_end": "now"}
  
As you can see in the second example, the field "time_end" is set to "now". This means that the server take the current UTC +- 0 time.

## Installation:

### General:
##### Gateway:
The gateway forwards all incoming messages under sensorbases/ to the server. Furthermore, it receives all other messages from all other gateways of a user by default. This can be adjusted in the mosquitto.conf file. A user friendly web environment for configuration of the gateway is under development.

##### server: 
The installation includes Eclipse Mosquitto as broker, Django as web framework and Inlfuxdb as database. Optionally, nginx and gunicorn can be installed and configured as web servers.

##### Encryption: 
Originally, encryption was implemented using Openssl, but at the moment the focus is on let's encrpypt as certificate authority. Which is also accepted by the common browsers.

### Requirements: 

The setup was tested on Debian 9/10 and Rpi 3B+ / 4.

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
cd IoTree42/IoTree_dir 
```

### setup.sh
Install with sudo bash setup.sh.

For a complete setup, this includes an SSL certificate setup provided by Let's encrypt and Nginx as web server.
Please check after instalation if Gateway ZIP file has a PEM included.
Also check if DNS in /etc/iotree/config.json is OK.
If you plan to use own certs, Jan-Piet Mens CA generator would be a good start. -> https://github.com/owntracks/tools/tree/master/TLS 
The script is also included in the IoTree folder...
#### NOTE: please setup the certs befor running setup.sh using certbot!
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
At the end add this line.
```
@reboot bash /etc/iotree/reload3.sh
```
save and close it.

### Installations of python modules and test.
```
cd ~/iot42 
```
install all the requirements.

```
virtualenv -p python3 venv1
source venv1/bin/activate
pip3 install -r requirements.txt
```
do the same for the Django requirements.
```
cd ~/dj_iot
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
cd ~/iot42
```
start the mqttodb1.py in the background without nohup.out:
```
source venv1/bin/activate
nohup python3 mqttoinflux1.py </dev/null >/dev/null 2>&1 &
```
Now start the django server without nginx:
```
cd ~/dj_iot
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
It is recommended to do everything on an Nginx server.
You may also want to install a firewall like ufw for security.
and if you have a DNS name, lets encrypt would be a good choice.


## Testing of Server performance
Under the order "testing" is a python script which puts a stress test on the server.

## Rest API
### some API examples are found here:
for [python](https://github.com/IoTree/IoTree42/tree/master/API_examples)
for [R](https://github.com/IoTree/IoTree42/tree/master/API_examples)

## FAQs
#### Is it possible to use only the Mqtt-broker?
  -	Yes, it is. The permission for your specific topic is set to read and write. 
  -	Just subscribe your topic (example: gateways/-your-mqtt-username-/...), with all the necessary
information (certificates, user, topic, password, host, port).
#### Is my data secure?
  -	Yes and no. your data can theoretically be seen by the admin.
  -	Your profile pic can be seen from everyone who has access to this site.
  -	The use of IoTree42 is at your own risk.
#### Can the Gateway itself be also a Sensorbase?
  -	Yes, just program your script as if it were on a different Raspberry Pi.
#### Can I delete all my data?
  -	Yes, when you delete your account everything stored related to you will be deleted.
#### Can I use other devices as gateway than a Raspberry pi?
  -	Yes, as long as the device can run mosquitto borker, but Cputemp.py might not work.
  -	When you install it manualy you will need to stor the .pem certificate in the right directory an change the config file of mosquitto broker.
#### Can I send data from 2 gateways, which will then be displayed as one?
  -	You need to set the same ID for both.
#### Can I set up a gateway as a subgetaway?
  -	Yes, you'll need to modify mosquitto.conf file so that the data is sent to the first gateway. 
#### I would like to extend my measurement with a new sensor. Can I use the already used topic?
  -	Yes, you can. Just expand your JSON string with a new field and a value.
  -	Do not delete other fields. This can cause problems because some data will not be displayed. Send instead zeros.

#### My Mqtt-password has been stolen what should I do?
  -	Contact admin
#### Data is not displayed!
  -	If you just registered the server/admin will need some time to set up everything for you. Try it later again.
  -	Make sure your using global time UTC +-0
  -	Make sure your json string is valid. Can be tested here.
  -	Make sure your gateway has internet connection.
  -	Make sure your mqtt username and password is set correctly.
#### Timestamp is displaying something around 1970.
  - Your sensorbase likely do not have the global time so it starts with UNIX time = 0 sec,
    which is equal to 01.01.1970 00:00:00 in human readable time.
#### I cannot log in!
  -	Contact admin
#### Raspberry Pi doesn't get any connection to server.
  -	Check internet connection.
  -	Check your config.json file.
  -	Check your power.
  -	Or contact Admin.
#### Some data is missing.
  - Look at FAQs “I would like to extend…”
  - Is your JSON-string correct.
  - Dose your sensor works correctly


## At last:

There is NO WARRANTY or guarantee FOR LOUSING DATA on both sides, server and gateway.
The operator takes NO RESPON on anything. THE USE of IoTree42 and anything related to it, IS ON YOUR OWN RISK.


### Found some bugs?
Contact me

