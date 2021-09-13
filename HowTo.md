## How To:

### General:
##### server: 
The installation includes Eclipse Mosquitto as broker, Django as web framework and Inlfuxdb as database. Optionally, nginx and gunicorn can be installed and configured as web servers.

##### Gateway:
The gateway forwards all incoming messages under the MQTT-Topic "universe/#" to the Platform.
instructions and instaltion files to setup upa gateway are downlaoded from the server once it deployd and running.

##### Encryption: 
Originally, encryption was implemented using Openssl, but at the moment the focus is on let's encrpypt as certificate authority. Which is also accepted by the common browsers.


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
  -	Always use "universe/" before the sub-topic. Otherwise it will not be processed through the gateway.
  
Example topic: universe/luxsensor/tls2591

### Visualize or to check the incoming data

#### Your IoTree:
  Click on “Your IoTree”.
  ![alt text](https://github.com/IoTree/IoTree42/blob/master/.gitignore/query_data2.png)
  1.	The tree structure corresponds to the MQTT topic defined in your sensor host (e.g. microcontroller with attached sensors) and gateway.
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
  {"tree": "gateway1/gatewayself/cputemp", "time_start":"0", "time_end":"1559187967000"}
  
#### Or like this:
  {"tree": "gateway1/gatewayself/cputemp,LUXSensor/tls2591", "time_start":"1559187967000", "time_end": "now"}
  
As you can see in the second example, the field "time_end" is set to "now". This means that the server take the current UTC +- 0 time.

