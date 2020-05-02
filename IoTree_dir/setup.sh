#!/bin/bash


# chacking for flags
x=$1
y=$2
ssl=false
nginx=false
if [ "$x" = "--ssl" ]; then
  ssl=true
fi
if [ "$x" = "--nginx" ]; then
  nginx=true
fi
if [ "$y" = "--ssl" ]; then
  ssl=true
fi
if [ "$y" = "--nginx" ]; then
  nginx=true
fi



# entrys
echo "******************************************"
echo "*  _____   _______            _  _ ___   *"
echo "* |_   _| |__   __|          | || |__ \  *"
echo "*   | |  ___ | |_ __ ___  ___| || |_ ) | *"
echo "*   | | / _ \| | '__/ _ \/ _ \__   _/ /  *"
echo "*  _| || (_) | | | |  __/  __/  | |/ /_  *"
echo "* |_____\___/|_|_|  \___|\___|  |_|____| *"
echo "*                                        *"
echo "******************************************"
echo "<<<-----     Hallo to IoTree42      --->>>"
echo "ENTER YOUR LINUX USERNAME FOR BUIDING PATHS"
read myvariable
echo "<<<--          SETUP DJANGO          -->>>"
echo "ENTER AN EMAIL, for sending the password reset url"
read sendingmail
echo "ENTER PASSWORD FOR THIS EMAIL, for sending the password reset url. !HIDDEN INPUT!"
read -s sendingpass
echo "ENTER ADMINMAIL, for resiving notivications form server"
read adminmail

# istalling all nessery programms
# sudo apt-get update
# sudo apt-get -y upgrade
apt-get install -y python3-pip
apt-get install -y curl
python3 -m pip install --user virtualenv
apt install virtualenv python3-virtualenv
apt install -y mosquitto mosquitto-clients
if [ "$nginx" = true ]; then
apt install -y nginx
fi
apt-get install -y influxdb
apt install -y influxdb-client
apt-get install -y inotify-tools
apt-get install -y libopenjp2-7
apt install -y libtiff5
apt-get install -y zip
# installing grafana
apt-get install -y adduser libfontconfig1
wget https://dl.grafana.com/oss/release/grafana_6.6.2_amd64.deb
PATH=$PATH:/sbin
dpkg -i grafana_6.6.2_amd64.deb



# get linux username make password for mqtt, get host IP ....
mqttpass=$(</dev/urandom tr -dc '0123456789ABZDEFGHIJKLMOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' | head -c12)
serverip=$(ip addr | grep 'state UP' -A2 | tail -n1 | awk '{print $2}' | cut -f1  -d'/')
hostname=$(hostname)
if [ -z "$myvariable" ]
then
    myvariable=$(who am i | awk '{print $1}')
fi
if [ -z "$sendingmail" ]
then
    sendingmail=defaultsendig
fi
if [ -z "$sendingpass" ]
then
    sendingpass=defaultpass
fi
if [ -z "$adminmail" ]
then
    adminmail=defaultadmin
fi

#generate pw for influx: admin, fluxcondj, mqttodb,
fluxadmin=$(</dev/urandom tr -dc '0123456789ABZDEFGHIJKLMOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' | head -c32)
fluxcondj=$(</dev/urandom tr -dc '0123456789ABZDEFGHIJKLMOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' | head -c32)
fluxmqttodb=$(</dev/urandom tr -dc '0123456789ABZDEFGHIJKLMOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' | head -c32)

#generate pw for grafana admin
grafadmin=$(</dev/urandom tr -dc '0123456789ABZDEFGHIJKLMOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' | head -c20)

#generate django key
djangokey=$(</dev/urandom tr -dc '0123456789!@#$%^&*()_=+abcdefghijklmnopqrstuvwxyz' | head -c50)

mkdir ./tmp
# build mosquitto.conf file
if [ "$ssl" = true ]; then
./bin/tmp.mosquitto.conf.ssl.sh $serverip > ./tmp/mosquitto.conf
else
./bin/tmp.mosquitto.conf.nossl.sh > ./tmp/mosquitto.conf
fi
chmod -R 644 ./tmp/mosquitto.conf


# building nginx config file
if [ "$nginx" = true ]; then
./bin/tmp.nginx-ssl.sh $myvariable $serverip > ./tmp/nginx-ssl.conf
./bin/tmp.nginx-nossl.sh $myvariable $serverip > ./tmp/nginx-nossl.conf
fi

# building gunicorn config file: service and sockets
if [ "$nginx" = true ]; then
./bin/tmp.gunicorn.service.sh $myvariable > ./tmp/gunicorn.service
./bin/tmp.gunicorn.socket.sh > ./tmp/gunicorn.socket
fi

# building grafana config file
./bin/tmp.grafana.ini.sh > ./tmp/grafana.ini

# building indluxdb config file
./bin/tmp.influxdb.conf.sh > ./tmp/influxdb.conf

#build config.json file for django
if [ "$nginx" = true ]; then
grafaaddress="/grafana/"
else
grafaaddress="http://$serverip:3000"
fi

./bin/tmp.config.json.sh $myvariable $serverip $adminmail $sendingmail $sendingpass $djangokey $serverip $fluxadmin $fluxmqttodb $fluxcondj $grafadmin $grafaaddress $hostname $mqttpass > ./tmp/config.json

# build hash3.sh file
./bin/tmp.hash3.sh > ./tmp/hash3.sh

# build reload3.sh file
./bin/tmp.reload3.sh > ./tmp/reload3.sh


# building gateway zip file
if [ "$ssl" = true ]; then
cp ./home_user/ssl/client/* ./IoTree_Gateway
fi
zip -r IoTree_Gateway_V_1.1.zip ./IoTree_Gateway
mv ./IoTree_Gateway_V_1.1.zip ./home_user/dj_iot/media/downloadfiles


# move all files and folders to destination
mkdir /etc/iotree
cp -r ./home_user/* /home/$myvariable/
cp /etc/mosquitto/mosquitto.conf /etc/mosquitto/mosquitto.conf.iotree_save
cp -r ./tmp/mosquitto.conf /etc/mosquitto/mosquitto.conf
cp /etc/influxdb/influxdb.conf /etc/influxdb/influxdb.conf.iotree_save
cp -r ./tmp/influxdb.conf /etc/influxdb/influxdb.conf
cp -r ./tmp/config.json /etc/iotree
cp -r ./tmp/hash3.sh /etc/iotree
cp -r ./tmp/reload3.sh /etc/iotree
cp -r ./tmp/gunicorn.service /etc/systemd/system
cp -r ./tmp/gunicorn.socket /etc/systemd/system
if [ "$nginx" = true ]; then
cp -r ./tmp/nginx-ssl.conf /etc/nginx/sites-available/nginx-ssl.conf
cp -r ./tmp/nginx-nossl.conf /etc/nginx/sites-available/nginx-nossl.conf
cp /etc/grafana/grafana.ini /etc/grafana/grafana.ini.iotree_save
cp -r ./tmp/grafana.ini /etc/grafana/grafana.ini
else
cp -r ./tmp/grafana.ini /etc/grafana/grafana.ini.iotree
fi

# building files acl, hashing, passwd
touch /etc/iotree/.acl
touch /etc/iotree/.hashing
touch /etc/iotree/.passwd

# secure files
chmod -R 744 /etc/iotree/config.json
chmod -R 766 /etc/iotree/.acl
chmod -R 766 /etc/iotree/.hashing
chmod -R 766 /etc/iotree/.passwd
chown $myvariable:$myvariable /home/$myvariable/dj_iot
chown $myvariable:$myvariable /home/$myvariable/iot42
chmod -R 766 /home/$myvariable/dj_iot/db.sqlite3
chmod 764 /home/$myvariable/dj_iot

# setup mosquitto broker user
mosquitto_passwd -b /etc/iotree/.passwd mqttodb $mqttpass

# making influxdb user: fluxcondj, mqttodb, admin (all privileged),
curl "http://localhost:8086/query" --data-urlencode "q=CREATE USER fluxcondj WITH PASSWORD '$fluxcondj'"
curl "http://localhost:8086/query" --data-urlencode "q=CREATE USER mqttodb WITH PASSWORD '$fluxmqttodb'"
curl "http://localhost:8086/query" --data-urlencode "q=CREATE USER admin WITH PASSWORD '$fluxadmin' WITH ALL PRIVILEGES"


# start services:
systemctl daemon-reload
systemctl enable grafana-server
systemctl restart grafana-server
systemctl restart influxdb
if [ "$nginx" = true ]; then
systemctl start gunicorn
systemctl enable gunicorn
systemctl reload nginx
fi

if [ "$nginx" = true ]; then
if [ "$ssl" = true ]; then
ln -s /etc/nginx/sites-available/nginx-ssl.conf /etc/nginx/sites-enabled/
else
ln -s /etc/nginx/sites-available/nginx-nossl.conf /etc/nginx/sites-enabled/
fi
rm -r /etc/nginx/sites-enabled/default
fi


# making grafana user: admin
sleep 10
grafana-cli admin reset-admin-password $grafadmin
