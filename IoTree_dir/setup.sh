#!/bin/bash


# chacking for flags
x=$1
y=$2
nossl=false
samesame=false
if [ "$x" = "nossl" ]; then
  nossl=true
fi
if [ "$x" = "samesame" ]; then
  samesame=true
fi
if [ "$y" = "nossl" ]; then
  nossl=true
fi
if [ "$y" = "samesame" ]; then
  samesame=true
fi

# istalling all nessery programms
# sudo apt-get update
# sudo apt-get -y upgrade
sudo apt install -y python3-pip
sudo apt-get install -y openssl
# install mongodb 2.7 or later
sudo apt install -y mosquitto
sudo apt install -y mosquitto mosquitto-clients
sudo apt-get install -y inotify-tools
sudo apt-get install -y libopenjp2-7
sudo apt install -y libtiff5
sudo apt-get install -y zip
python3 -m pip install --user virtualenv


# get linux username make password for mqtt get host IP
mqttpass=$(</dev/urandom tr -dc '0123456789ABZDEFGHIJKLMOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' | head -c12)
serverip=$(hostname -I)
serverip="${serverip//[[:space:]]/}"
echo "enter your linux username for building directorys"
echo "or live it emty but mide not work"
read myvariable
if [ -z "$myvariable" ]
then
    myvariable=$(who am i | awk '{print $1}')
fi

# setup mosquitto broker
mosquitto_passwd -b ./home_user/passwd mqttodb $mqttpass

if [ "$nossl" = false ]; then
# making and storing the ssl certificates
echo '!!!the following inputs are for the openssl certificates!!!'

openssl req -new -x509 -days 365 -extensions v3_ca -keyout ca.key -out ca.crt
openssl genrsa -out server.key 2048
openssl req -out server.csr -key server.key -new
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 364
openssl genrsa -out client.key 2048
openssl req -out client.csr -key client.key -new
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 364

mv ca.key ./home_user/ssl/secrets
cp ca.crt ./home_user/ssl/client
mv ca.crt ./home_user/ssl/server
mv server.key ./home_user/ssl/server
mv server.crt ./home_user/ssl/server
mv client.crt ./home_user/ssl/client
mv client.key ./home_user/ssl/client
rm -r ca.srl client.csr server.csr
fi

# build mosquitto.conf file
if [ "$nossl" = false ]; then
echo 'port 8883' >>./etc/mosquitto/mosquitto.conf
string="cafile /home/${myvariable}/.ssl/server/ca.crt"
echo ${string} >>./etc/mosquitto/mosquitto.conf
string="certfile /home/${myvariable}/.ssl/server/server.crt"
echo ${string} >>./etc/mosquitto/mosquitto.conf
string="keyfile /home/${myvariable}/.ssl/server/server.key"
echo ${string} >>./etc/mosquitto/mosquitto.conf
else
echo 'port 1883' >>./etc/mosquitto/mosquitto.conf
fi
echo 'allow_anonymous false' >>./etc/mosquitto/mosquitto.conf
string="password_file /home/${myvariable}/.passwd"
echo ${string} >>./etc/mosquitto/mosquitto.conf
string="acl_file /home/${myvariable}/.acl"
echo ${string} >>./etc/mosquitto/mosquitto.conf

chmod -R 644 ./etc/mosquitto/mosquitto.conf

# build hash3.sh file
echo '#!/bin/sh' >>./etc/mosquitto/hash3.sh
echo '' >>./etc/mosquitto/hash3.sh
string="/home/${myvariable}/.passwd"
echo MQTT_PASS_PATH='"'${string}'"' >>./etc/mosquitto/hash3.sh
string="/home/${myvariable}/.hashing"
echo MQTT_HASH_PATH='"'${string}'"' >>./etc/mosquitto/hash3.sh
echo '' >>./etc/mosquitto/hash3.sh
echo 'while inotifywait -e close_write $MQTT_HASH_PATH; do' >>./etc/mosquitto/hash3.sh
echo '   if [ -s $MQTT_HASH_PATH ]' >>./etc/mosquitto/hash3.sh
echo '   then' >>./etc/mosquitto/hash3.sh
echo '      mosquitto_passwd -U $MQTT_HASH_PATH' >>./etc/mosquitto/hash3.sh
echo '      cat $MQTT_HASH_PATH >> $MQTT_PASS_PATH' >>./etc/mosquitto/hash3.sh
echo '      > $MQTT_HASH_PATH' >>./etc/mosquitto/hash3.sh
echo '      #PID="$(pidof mosquitto)"' >>./etc/mosquitto/hash3.sh
echo '      #kill -SIGHUP $PID' >>./etc/mosquitto/hash3.sh
echo '   else' >>./etc/mosquitto/hash3.sh
echo '      echo ""' >>./etc/mosquitto/hash3.sh
echo '   fi' >>./etc/mosquitto/hash3.sh
echo 'done' >>./etc/mosquitto/hash3.sh

# build reload3.sh file
echo '#!/bin/sh' >>./etc/mosquitto/reload3.sh
echo '' >>./etc/mosquitto/reload3.sh
echo '' >>./etc/mosquitto/reload3.sh
string="/home/${myvariable}/.passwd"
echo MQTT_PASS_PATH='"'${string}'"' >>./etc/mosquitto/reload3.sh
echo 'while inotifywait -e close_write $MQTT_PASS_PATH; do' >>./etc/mosquitto/reload3.sh
echo '   PID="$(pidof mosquitto)"' >>./etc/mosquitto/reload3.sh
echo '   kill -SIGHUP $PID' >>./etc/mosquitto/reload3.sh
echo 'done' >>./etc/mosquitto/reload3.sh

#build config.json file for django
echo "<-- setup your django configs -->"
echo "-- enter a mail, for sending the password reset url. tested with Google mail --"
echo "-- if you have no sudiple mail accunt live empty the restet funktion is not avalable then --"
read sendingmail
echo "-- enter the password mail acaunt, for sending the password reset url --"
echo "--!! hidden input !!--"
read -s sendingpass
echo "-- enter your mail for resiving notivications form server --"
read adminmail
djangokey=$(</dev/urandom tr -dc '0123456789!@#$%^&*()_=+abcdefghijklmnopqrstuvwxyz' | head -c50)
echo '{' >>./etc/config.json
echo '"'SENDING_MAIL'"':'"'$sendingmail'"', >>./etc/config.json
echo '"'SENDING_PASS'"':'"'$sendingpass'"', >>./etc/config.json
echo '"'ADMIN_MAIL'"':'"'$adminmail'"', >>./etc/config.json
echo '"'DJANGO_SECRET_KEY'"':'"'$djangokey'"', >>./etc/config.json
echo '"'MANGO_ADRESS'"':'"'mongodb://localhost:27017/'"', >>./etc/config.json
echo '"'MANGO_DATA_COL'"':'"'SensorData'"', >>./etc/config.json
echo '"'MANGO_DATABASE'"':'"'iot42'"', >>./etc/config.json
echo '"'HOST_IP'"':'"'$serverip'"', >>./etc/config.json
echo '"'MQTT_ACL_PATH'"':'"'/home/$myvariable/.acl'"', >>./etc/config.json
echo '"'MQTT_HASH_PATH'"':'"'/home/$myvariable/.hashing'"', >>./etc/config.json
echo '"'MQTT_PASS_PATH'"':'"'/home/${myvariable}/.passwd'"', >>./etc/config.json
echo '"'MQTT_IP'"':'"'${serverip}'"', >>./etc/config.json
if [ "$nossl" = false ]; then
  echo '"'MQTT_PORT'"':'"'8883'"', >>./etc/config.json
  echo '"'CLIENT_CERT'"':'"'/home/${myvariable}/.ssl/client/client.crt'"', >>./etc/config.json
  echo '"'CLIENT_CA'"':'"'/home/${myvariable}/.ssl/client/ca.crt'"', >>./etc/config.json
  echo '"'CLIENT_KEY'"':'"'/home/${myvariable}/.ssl/client/client.key'"', >>./etc/config.json
else
  echo '"'MQTT_PORT'"':'"'1883'"', >>./etc/config.json
  echo '"'CLIENT_CERT'"':'"''"', >>./etc/config.json
  echo '"'CLIENT_CA'"':'"''"', >>./etc/config.json
  echo '"'CLIENT_KEY'"':'"''"', >>./etc/config.json
fi
echo '"'MQTT_TODB_NAME'"':'"'mqttodb'"', >>./etc/config.json
echo '"'MQTT_TODB_PASS'"':'"'${mqttpass}'"' >>./etc/config.json
echo '}' >>./etc/config.json


# building gateway zip file
cp ./home_user/ssl/client/* ./IoTree_Gateway/ssl
echo '{' >>./IoTree_Gateway/.config.json
echo '"'SERVER_IP'"':'"'${serverip}'"', >>./IoTree_Gateway/.config.json
if [ "$nossl" = false ]; then
  echo '"'SERVER_PORT'"':'"'8883'"', >>./IoTree_Gateway/.config.json
  echo '"'CA_PATH'"':'"'./.ssl/ca.crt'"', >>./IoTree_Gateway/.config.json
  echo '"'CERT_PATH'"':'"'./.ssl/client.crt'"', >>./IoTree_Gateway/.config.json
  echo '"'KEY_PATH'"':'"'./.ssl/client.key'"', >>./IoTree_Gateway/.config.json
else
  echo '"'SERVER_PORT'"':'"'1883'"', >>./IoTree_Gateway/.config.json
  echo '"'CA_PATH'"':'"''"', >>./IoTree_Gateway/.config.json
  echo '"'CERT_PATH'"':'"''"', >>./IoTree_Gateway/.config.json
  echo '"'KEY_PATH'"':'"''"', >>./IoTree_Gateway/.config.json
fi
echo '"'MQTT_USERNAME'"':'"''"', >>./IoTree_Gateway/.config.json
echo '"'MQTT_PASSWORD'"':'"''"' >>./IoTree_Gateway/.config.json
echo '}' >>./IoTree_Gateway/.config.json
mv ssl .ssl
zip -r IoTree_Gateway_V_1.1.zip ./IoTree_Gateway
mv ./IoTree_Gateway_V_1.1.zip ./home_user/dj_iot/media/downloadfiles


# move all files and folders to destination
mv -v ./home_user/ssl/* /home/$myvariable/.ssl
mv ./home_user/acl /home/$myvariable/.acl
mv ./home_user/passwd /home/$myvariable/.passwd
mv ./home_user/hashing /home/$myvariable/.hashing
mv -v ./home_user/* /home/$myvariable/
mv /etc/mosquitto/mosquitto.conf /etc/mosquitto/mosquitto.conf.iotree_save
mv -v ./etc/mosquitto/* /etc/mosquitto/
mv ./etc/config.json /etc


# secure files
chmod -R 700 /home/$myvariable/.ssl/secrets
chmod -R 744 /home/$myvariable/.ssl/client
chmod -R 744 /home/$myvariable/.ssl/server
chmod -R 744 /etc/config.json

# delete all install files
rm -r ../IoTree_dir

# restart services
service mosquitto restart

