# IoTree42
## How it works
The basic is Structure is illustrated below.
![alt text](https://github.com/IoTree/IoTree42/blob/master/.gitignore/in_a_nutshell.png)

## How to use:

### First you need to set up a gateway.

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
  -	Always use "sensorbases/" before the sub-topic. Otherwise it will not be processed through the gateway.
  
Example topic: sensorbases/luxsensor/tls2591

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
  curl --header "Content-Type: application/json" --request POST --data '{"username":"xyz","password":"xyz"}' https://<server address>/api-token-auth/

Then you connect your applications with Rest-Api trough the link "<server ad.>/iotree_api".
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


## more FAQs:

#### Is it possible to use only the Mqtt-broker?
  -	Yes, it is. The permission for your specific topic is set to read and write. 
  -	Just subscribe your topic (example: gateways/<your mqtt username>/...), with all the necessary
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

## Difficulties?

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

## Limitations:
  -	This platform can not handle time critical stuff.
  -	Max payload size : 20MB
  -	Milliseconds are the minimum time interval
  -	No nested Array or Object.

## Upcoming features
### In near future:
  -	RStudio integration on server for data processing.
  -	Python integration on server for data processing.
  -	Online Lib with code snippets from users.
    o	For example, from new sensorbases or sensors.
  - time critical connections.
  - detailed Documentation

## At last:

There is NO WARRANTY or guarantee FOR LOUSING DATA on both sides, server and gateway.
The operator takes NO RESPON on nything. THE USE of this platform IoTree42 and anything related to it, IS ON YOUR ON RISK.


### Found some bugs?
Contact me or on GitHub.

And as always: learning by doing.
