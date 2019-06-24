# IoTree42
## How it works
The basic is Structure is illustrated below.
![alt text](https://github.com/IoTree/IoTree42/blob/master/github/in_a_nutshell.png)

## How to use:

### First you need to set up a gateway.

For this look at follow the link to Setting up my RPi.
If you want to use a different sensor base like Arduino,
you need to know your IP of the gateway or its hostname
Sometimes hostname won’t work. It depends on the DHCP-Server in this network
As mentioned in Setting up my RPi you can use the python script cputemp.py for testing.
If everything is running and gateway is displaying 2 times “Connection OK”,
it should work and your data will reach the server.

### To visualize or to check the incoming data you have two modes.

#### The fast Mode:
  Just click on the button “iotree” in the blue box.
  Now you can choose between your gateways.
  Submit, and then you will see all topics or sensors, if you like.
  You can choose to download the data or display it in a chart or simple table.
  All options include all dates from the beginning.

To limit the time or simply to list more than one sensor base from a gateway, you can use the detail mode.

#### The detailed Mode:
  You can use the second mode with a click on “inquiry”.
  ![alt text](https://github.com/IoTree/IoTree42/blob/master/github/query_data.png)
  There you have multiple option to query your data.
  1.	Choose your Gateway.
  2.	The tree structure corresponds to the MQTT topic defined in your sensor base.
      For example, you have an MQTT topic like this: "sensorbase / feather01 / tsl2591" 
      and just want to display this data. For this you can enter "feather01, tsl2591" for example.
  3.	And   
  4.  Are setting the start and end point.
  5.	When set to “tree” only the tree branches will be shown. This might be helpful when there are a lot of Sensorbases.
  6.	This refers to point 2. Here you can specify whether or not the tree branch follows a specific order.
  Let's say you have these mqtt-topics:
    -	sensorbase/feather01/tsl2591
    -	sensorbase/feather01/tsl2591_2
    -	sensorbase/feather03/tsl2591
    -	sensorbase/feather01/dht22
  Now if you want all the data with "tsl2591", just type "tsl2591" and do not put hook. You will get all the data from:
  sensorbase/feather01/tsl2591 and sensorbase/feather03/tsl2591.
  It is that easy!
  7.	When you set this choose you simply negated the tree branch. This means if you have the same data as in point 3 and you enter “tsl2591” in point 2 and also undo the hook in point3, you will get the data from "sensorbase/feather01/tsl2591_2" and "sensorbase/feather01/dht22".
  8.	Select if you want to download a CSV file or view a spreadsheet or chart.
  
### Rest API

You can connect your applications with Rest-Api trough the page "https:/++++.it". You need to be logged in.
First all your gateway IDs will be sent. Then you can do your queries, with the same possibilities and filters as on the "inquiry" page. The json string is declared as follows:

  {"gateway_id": "One of your gateway IDs has been sent to you."
  "Tree": "the branch divided by" _ ",
  "Filter": "data or tree",
  "in_order": "is the branch in an order? ",
  "negates": "Should the branch be negated?",
  "time_start": "start of interval in milliseconds",
  "time_end": "End of interval in milliseconds"}.
  
And a POST can look like this:
  {"gateway_id": "inku", "tree": "", "filters": "data", "in_order": "True", "negated": "False", "time_start":"0",   "time_end":"1559187967000"}
  
Or like this:
  {"gateway_id":"000000345ba23", "tree":"", "filters": "tree", "in_order": "False", "negated": "True", "time_start":"1559187967000", "time_end": "now"}
  
As you can see in the second example, the field "time_end" is set to "now". This means that the server take the current UTC +- 0 time.

## Rules for use

Be sure your Raspberry Pi is up to date and secure with a proper password!

### Important rules for the dataset | object | payload:
  -	It must be in proper JSON-format. If not so it won’t be stored.
  -	Timestamps must be in UNIX-Format. Also the field key needs a form of “time”, “Zeit” or ”UNIX” in it. For example: “timestamp” or “Zeiten” would also work. This is necessary for the server to display the timestamp in human readable time.
  -	Use global time UTC +-0.
  -	Don’t use nested objects or Arrays.
  -	Do not send multiple JSON strings at once. Send them individually.
  -	Max time increment is 1 millisecond.
  -	Save measurement values as integer not as string.
Example payload: {“sensor”: ”tsl2591”, “lux”: 2314, “time”: 1561373832}

### Important rules for the topic:
  -	For simplicity only alphanumeric and “-“ characters are allowed. If not, so wrong characters will be deleted.
  -	Choose your topic and subtopic-levels wisely. So that you can find data later easily.
  -	Always use "sensorbase/" before the sub-topic. Otherwise it will not be processed through the gateway.

## FAQs:

#### Is it possible to use only the Mqtt-broker?
  -	Yes, it is. The permission for your specific topic is set to read and write. 
  -	Just subscribe your topic (example: gateways/your mqtt username/...), with all the necessary
information (certificates, user, topic, password, host, port).
#### Is my data secure?
  -	Yes and no. your data is not stored encrypted and theoretically it can be seen form the admin.
  -	Your profile pic can be seen from everyone who has access to this site.
  -	The use of IoTree42 is at your own risk.
#### Can the Gateway itself be also a Sensorbase?
  -	Yes, just program your script as if it were on a different Raspberry Pi.
#### Can I delete my data?
  -	Yes, when you delete your account everything stored related to you will be deleted.
  -	In the Future there will be a function to deleted specific data.
#### Can I use other devices as gateway than a Raspberry pi?
  -	Yes, you can easily run the mqrrbridge1.py scripts on any Linux, but Cputemp.py might not work.
  -	If you want to run it on something else you will need the certificates form the “.ssl” folder.
#### Can I send data from 2 gateways, which will then be displayed as one?
  -	Yes, it is possible. In the “mqttbridge1.py” script there is the option to set a “gateway_id”.
  -	You need to set the same ID for both.
#### Can I set up a gateway as a subgetaway?
  -	Yes, you'll need to modify the mqttbridge1.py script a little so that the data is sent to the first gateway. 
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
  -	Data sharing with other user's.
  -	Own Password for your Database.
  -	"Deleting" Function.
  -	Dynamic Charts.
### in the distant future:
  -	MATLAB integration on server for data processing.
  -	Python integration on server for data processing.
  -	Online Lib with code snippets from users.
    o	For example, from new sensorbases or sensors.
  - time critical connections.

## At last:

There is NO WARRANTY or guarantee FOR LOUSING DATA on both sides, server and gateway.
The operator takes NO RESPON on anything. THE USE of this platform IoTree42 and anything related to it, IS ON YOUR ON RISK.


### Found some bugs?
Contact me or on GitHub.

And as always: learning by doing.
