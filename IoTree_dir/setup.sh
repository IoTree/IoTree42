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

python3 -m pip install --user virtualenv

# entrys
echo "<<<--- Hallo to IoTree42 --->>>"
echo "ENTER YOUR LINUX USERNAME FOR BUIDING PATHS"
read myvariable
echo "<-- SETUP DJANGO -->"
echo "ENTER AN EMAIL, for sending the password reset url"
read sendingmail
echo "ENTER PASSWORD FOR THIS EMAIL, for sending the password reset url"
echo "--!! hidden input !!--"
read -s sendingpass
echo "ENTER ADMINMAIL, for resiving notivications form server"
read adminmail

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


# get linux username make password for mqtt get host IP
mqttpass=$(</dev/urandom tr -dc '0123456789ABZDEFGHIJKLMOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' | head -c12)
serverip=$(hostname -I)
serverip="${serverip//[[:space:]]/}"
if [ -z "$myvariable" ]
then
    myvariable=$(who am i | awk '{print $1}')
fi

# setup mosquitto broker
mosquitto_passwd -b ./home_user/passwd mqttodb $mqttpass

# making and storing the ssl certificates
mkdir ./home_user/ssl
mkdir ./home_user/ssl/server
mkdir ./home_user/ssl/client
mkdir ./home_user/ssl/secrets
if [ "$nossl" = false ]; then
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
mkdir ./tmp
if [ "$nossl" = false ]; then
echo 'port 8883' >>./tmp/mosquitto.conf
string="cafile /home/${myvariable}/.ssl/server/ca.crt"
echo ${string} >>./tmp/mosquitto.conf
string="certfile /home/${myvariable}/.ssl/server/server.crt"
echo ${string} >>./tmp/mosquitto.conf
string="keyfile /home/${myvariable}/.ssl/server/server.key"
echo ${string} >>./tmp/mosquitto.conf
else
echo 'port 1883' >>./tmp/mosquitto.conf
fi
echo 'allow_anonymous false' >>./tmp/mosquitto.conf
string="password_file /home/${myvariable}/.passwd"
echo ${string} >>./tmp/mosquitto.conf
string="acl_file /home/${myvariable}/.acl"
echo ${string} >>./tmp/mosquitto.conf

chmod -R 644 ./tmp/mosquitto.conf

# build hash3.sh file
echo '#!/bin/sh' >>./tmp/hash3.sh
echo '' >>./tmp/hash3.sh
string="/home/${myvariable}/.passwd"
echo MQTT_PASS_PATH='"'${string}'"' >>./tmp/hash3.sh
string="/home/${myvariable}/.hashing"
echo MQTT_HASH_PATH='"'${string}'"' >>./tmp/hash3.sh
echo '' >>./tmp/hash3.sh
echo 'while inotifywait -e close_write $MQTT_HASH_PATH; do' >>./tmp/hash3.sh
echo '   if [ -s $MQTT_HASH_PATH ]' >>./tmp/hash3.sh
echo '   then' >>./tmp/hash3.sh
echo '      mosquitto_passwd -U $MQTT_HASH_PATH' >>./tmp/hash3.sh
echo '      cat $MQTT_HASH_PATH >> $MQTT_PASS_PATH' >>./tmp/hash3.sh
echo '      > $MQTT_HASH_PATH' >>./tmp/hash3.sh
echo '      #PID="$(pidof mosquitto)"' >>./tmp/hash3.sh
echo '      #kill -SIGHUP $PID' >>./tmp/hash3.sh
echo '   else' >>./tmp/hash3.sh
echo '      echo ""' >>./tmp/hash3.sh
echo '   fi' >>./tmp/hash3.sh
echo 'done' >>./tmp/hash3.sh

# build reload3.sh file
echo '#!/bin/sh' >>./tmp/reload3.sh
echo '' >>./tmp/reload3.sh
echo '' >>./tmp/reload3.sh
string="/home/${myvariable}/.passwd"
echo MQTT_PASS_PATH='"'${string}'"' >>./tmp/reload3.sh
echo 'while inotifywait -e close_write $MQTT_PASS_PATH; do' >>/reload3.sh
echo '   PID="$(pidof mosquitto)"' >>./tmp/reload3.sh
echo '   kill -SIGHUP $PID' >>./tmp/reload3.sh
echo 'done' >>./tmp/reload3.sh

#build config.json file for django
djangokey=$(</dev/urandom tr -dc '0123456789!@#$%^&*()_=+abcdefghijklmnopqrstuvwxyz' | head -c50)
echo '{' >>./tmp/config.json
echo '"'SENDING_MAIL'"':'"'$sendingmail'"', >>./tmp/config.json
echo '"'SENDING_PASS'"':'"'$sendingpass'"', >>./tmp/config.json
echo '"'ADMIN_MAIL'"':'"'$adminmail'"', >>./tmp/config.json
echo '"'DJANGO_SECRET_KEY'"':'"'$djangokey'"', >>./tmp/config.json
echo '"'MANGO_ADRESS'"':'"'mongodb://localhost:27017/'"', >>./tmp/config.json
echo '"'MANGO_DATA_COL'"':'"'SensorData'"', >>./tmp/config.json
echo '"'MANGO_DATABASE'"':'"'iot42'"', >>./tmp/config.json
echo '"'HOST_IP'"':'"'$serverip'"', >>./tmp/config.json
echo '"'MQTT_ACL_PATH'"':'"'/home/$myvariable/.acl'"', >>./tmp/config.json
echo '"'MQTT_HASH_PATH'"':'"'/home/$myvariable/.hashing'"', >>./tmp/config.json
echo '"'MQTT_PASS_PATH'"':'"'/home/${myvariable}/.passwd'"', >>./tmp/config.json
echo '"'MQTT_IP'"':'"'${serverip}'"', >>./tmp/config.json
if [ "$nossl" = false ]; then
  echo '"'MQTT_PORT'"':'"'8883'"', >>./tmp/config.json
  echo '"'CLIENT_CERT'"':'"'/home/${myvariable}/.ssl/client/client.crt'"', >>./tmp/config.json
  echo '"'CLIENT_CA'"':'"'/home/${myvariable}/.ssl/client/ca.crt'"', >>./tmp/config.json
  echo '"'CLIENT_KEY'"':'"'/home/${myvariable}/.ssl/client/client.key'"', >>./tmp/config.json
else
  echo '"'MQTT_PORT'"':'"'1883'"', >>./tmp/config.json
  echo '"'CLIENT_CERT'"':'"''"', >>./tmp/config.json
  echo '"'CLIENT_CA'"':'"''"', >>./tmp/config.json
  echo '"'CLIENT_KEY'"':'"''"', >>./tmp/config.json
fi
echo '"'MQTT_TODB_NAME'"':'"'mqttodb'"', >>./tmp/config.json
echo '"'MQTT_TODB_PASS'"':'"'${mqttpass}'"' >>./tmp/config.json
echo '}' >>./tmp/config.json


# building gateway zip file
mkdir ./IoTree_Gateway/.ssl
if [ "$nossl" = false ]; then
cp ./home_user/ssl/client/* ./IoTree_Gateway/.ssl
fi
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
zip -r IoTree_Gateway_V_1.1.zip ./IoTree_Gateway
mv ./IoTree_Gateway_V_1.1.zip ./home_user/dj_iot/media/downloadfiles


# move all files and folders to destination
mkdir /etc/iotree
mkdir /home/$myvariable/.ssl
cp -r ./home_user/ssl/* /home/$myvariable/.ssl
mv ./home_user/acl /home/$myvariable/.acl
mv ./home_user/passwd /home/$myvariable/.passwd
mv ./home_user/hashing /home/$myvariable/.hashing
cp -r ./home_user/* /home/$myvariable/
cp /etc/mosquitto/mosquitto.conf /etc/mosquitto/mosquitto.conf.iotree_save
cp -r ./tmp/mosquitto.conf /etc/mosquitto/mosquitto.conf
cp -r ./tmp/config.json /etc/iotree
cp -r ./tmp/hash3.sh /etc/iotree
cp -r ./tmp/reload3.sh /etc/iotree


# secure files
chown -R $myvariable /home/$myvariable/.ssl
chmod -R 700 /home/$myvariable/.ssl/secrets
chmod -R 744 /home/$myvariable/.ssl/client
chmod -R 744 /home/$myvariable/.ssl/server
chmod -R 744 /etc/iotree/config.json

# delete all install files

# restart services
service mosquitto restart

