## FAQ
#### Is it possible to use only the Mqtt-broker?
  -	Yes, it is. The permission for your specific topic is set to read and write. 
  -	Just subscribe your topic (example: gateways/-your-mqtt-username-/...), with all the necessary
information (certificates, user, topic, password, host, port).
#### Is my data secure?
  -	Yes and no. your data can theoretically be seen by the admin.
  -	Your profile pic can be seen from everyone who has access to this site.
  -	The use of IoTree42 is at your own risk.
#### Can the Gateway itself be also a Sensorhost?
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
  - Your sensor host likely do not have the global time so it starts with UNIX time = 0 sec,
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