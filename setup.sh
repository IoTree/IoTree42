#!/bin/bash
set -e

# chacking for flags
x=$1
y=$2
full=false
local=false
nginx=true
if [ "$y" = "--nogninx"]; then
  nginx=false
fi
if [ "$x" = "--full" ]; then
  full=true
elif [ "$x" = "--raspberry" ]; then
  local=true
else
echo "no option set! Help for: sudo bash setup.sh [1. argument] [2. argument]"
echo "1. argument:"
echo "--full		full installation including https support and nginx"
echo "--raspberry	for a local installation e.g. on a Raspberry no SSL and other security settings are enabled, nginx is included."
echo "2. argument:"
echo "--nonginx		Nginx Webeserver and the Python WSGI HTTP Server gunicorn are NOT installed (not recommended)."
exit
fi



# inputs
echo "******************************************"
echo "*  _____   _______            _  _ ___   *"
echo "* |_   _| |__   __|          | || |__ \  *"
echo "*   | |  ___ | |_ __ ___  ___| || |_ ) | *"
echo "*   | | / _ \| | '__/ _ \/ _ \__   _/ /  *"
echo "*  _| || (_) | | | |  __/  __/  | |/ /_  *"
echo "* |_____\___/|_|_|  \___|\___|  |_|____| *"
echo "*                                        *"
echo "******************************************"
echo "<<<-----     SETUP OF IoTree42      --->>>"
echo "<<<-----      Version v0.4.1        --->>>"
echo "ENTER LINUX USERNAME FOR BUIDING PATHS"
read myvariable
echo "ENTER AN ADMIN PASSWORD !HIDDEN INPUT!"
read -s djangopass
#echo "<<<--          SETUP DJANGO          -->>>"
#echo "ENTER AN EMAIL, for sending the password reset url. You can leave it empty"
#read sendingmail
#echo "ENTER PASSWORD FOR THIS EMAIL, for sending the password reset url. !HIDDEN INPUT! You can leave it empty"
#read -s sendingpass
#echo "ENTER ADMINMAIL, for resiving notivications form server. You can leave it empty"
#read adminmail
#echo "ENTER ip, empty will try to read from system"
#read enteredip
if [ "$full" = true ]; then
echo "ENTER domain name for using TLS"
read domain
fi

# istalling all nessery programms
apt-get update
# sudo apt-get -y upgrade
apt-get install -y python3-pip
apt-get install -y curl
python3 -m pip install --user virtualenv
apt install -y virtualenv python3-virtualenv python3-appdirs python3-distlib python3-filelock
apt install -y mosquitto mosquitto-clients
if [ "$nginx" = true ]; then
  apt install -y nginx
fi
apt-get install -y inotify-tools
apt-get install -y libopenjp2-7
apt install -y libtiff5
apt-get install -y zip
# installing grafana #
sudo apt-get install -y adduser libfontconfig1
arch=$(uname -m)
arch2=${arch:0:3}
echo $arch
if [ "$arch2" = "arm" ]; then
echo "architecture: $arch"
wget https://dl.grafana.com/oss/release/grafana_8.0.6_armhf.deb
PATH=$PATH:/sbin
dpkg -i grafana_8.0.6_armhf.deb
wget https://dl.influxdata.com/influxdb/releases/influxdb-1.8.9_linux_armhf.tar.gz
tar xvfz influxdb-1.8.9_linux_armhf.tar.gz
elif [ "$arch2" = "amd" ]; then
echo "architecture: $arch"
wget https://dl.influxdata.com/influxdb/releases/influxdb_1.8.9_amd64.deb
sudo dpkg -i influxdb_1.8.9_amd64.deb
wget https://dl.grafana.com/oss/release/grafana_8.0.6_amd64.deb
PATH=$PATH:/sbin
dpkg -i grafana_8.0.6_amd64.deb
elif [ "$arch2" = "x86" ]; then
echo "architecture: $arch"
wget https://dl.influxdata.com/influxdb/releases/influxdb_1.8.9_amd64.deb
sudo dpkg -i influxdb_1.8.9_amd64.deb
wget https://dl.grafana.com/oss/release/grafana_8.0.6_amd64.deb
PATH=$PATH:/sbin
dpkg -i grafana_8.0.6_amd64.deb
else
echo "ERROR: invalid architecture '$arch' for Grafana or influxdb"
echo "Exit setup.sh please delete folder:"
echo "'/etc/iotree"
exit 1
fi

systemctl start influxdb
systemctl start grafana-server

# get linux username make password for mqtt, get host IP ....
mqttpass=$(</dev/urandom tr -dc '0123456789ABZDEFGHIJKLMOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' | head -c12)
serverip="$(ip addr | grep 'state UP' -A2 | tail -n1 | awk '{print $2}' | cut -f1  -d'/')"
hostname=$(hostname)
echo $hostname
if [ -z "$myvariable" ]
then
    myvariable=$(who am i | awk '{print $1}')
fi
if [ -z "$djangopass" ]
then
    djangopass="iotree42passchange"
fi
if [ -z "$sendingmail" ]
then
    sendingmail="none"
fi
if [ -z "$sendingpass" ]
then
    sendingpass="none"
fi
if [ -z "$adminmail" ]
then
    adminmail="none@none"
fi
if [ -z "$domain" ]
then
    domain=$hostname
fi
if [ -n "$enteredip" ]
then
    serverip=$enteredip
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
if [ "$full" = true ]; then
./lib/tmp.mosquitto.conf.ssl.sh $domain > ./tmp/mosquitto.conf
else
./lib/tmp.mosquitto.conf.nossl.sh > ./tmp/mosquitto.conf
fi
chmod -R 644 ./tmp/mosquitto.conf

if [ "$nginx" = true ]; then
# building nginx config file
./lib/tmp.nginx-ssl.sh $myvariable $domain > ./tmp/nginx-ssl.conf
./lib/tmp.nginx-nossl.sh $myvariable $serverip > ./tmp/nginx-nossl.conf

# building gunicorn config file: service and sockets
./lib/tmp.gunicorn.service.sh $myvariable > ./tmp/gunicorn.service
./lib/tmp.gunicorn.socket.sh > ./tmp/gunicorn.socket
fi

# building grafana config file
./lib/tmp.grafana.ini.sh > ./tmp/grafana.ini

# building indluxdb config file
./lib/tmp.influxdb.conf.sh > ./tmp/influxdb.conf

#build iotree config.json file
grafaaddress="/grafana/"


if [ "$full" = true ]; then
./lib/tmp.config.json.sh $myvariable $serverip $adminmail $sendingmail $sendingpass $djangokey $serverip $fluxadmin $fluxmqttodb $fluxcondj $grafadmin $grafaaddress $domain $mqttpass > ./tmp/config.json
else
./lib/tmp.config.json.sh $myvariable $serverip $adminmail $sendingmail $sendingpass $djangokey $serverip $fluxadmin $fluxmqttodb $fluxcondj $grafadmin $grafaaddress $hostname $mqttpass > ./tmp/config.json
fi

# build reload3.sh file
./lib/tmp.reload3.sh > ./tmp/reload3.sh


# building gateway zip file
if [ "$full" = true ]; then
cp /etc/ssl/certs/DST_Root_CA_X3.pem ./IoTree_Gateway
fi
zip -r IoTree_Gateway_V_2.0.zip ./IoTree_Gateway
mkdir ./home_user/dj_iot/media/downloadfiles
mv ./IoTree_Gateway_V_2.0.zip ./home_user/dj_iot/media/downloadfiles/


# move all files and folders to destination
mkdir /etc/iotree
cp -r ./home_user/* /home/$myvariable/
cp /etc/mosquitto/mosquitto.conf /etc/mosquitto/mosquitto.conf.iotree_save
cp -r ./tmp/mosquitto.conf /etc/mosquitto/mosquitto.conf
cp /etc/influxdb/influxdb.conf /etc/influxdb/influxdb.conf.iotree_save
cp -r ./tmp/influxdb.conf /etc/influxdb/influxdb.conf
cp -r ./tmp/config.json /etc/iotree
cp -r ./tmp/reload3.sh /etc/iotree
if [ "$nginx" = true ]; then
cp -r ./tmp/gunicorn.service /etc/systemd/system
cp -r ./tmp/gunicorn.socket /etc/systemd/system
cp -r ./tmp/nginx-ssl.conf /etc/nginx/sites-available/nginx-ssl-iotree.conf
cp -r ./tmp/nginx-nossl.conf /etc/nginx/sites-available/nginx-nossl-iotree.conf
cp /etc/grafana/grafana.ini /etc/grafana/grafana.ini.iotree_save
cp -r ./tmp/grafana.ini /etc/grafana/grafana.ini
else
cp -r ./tmp/grafana.ini /etc/grafana/grafana.ini.iotree
fi

# building files acl, passwd
touch /etc/iotree/.acl
touch /etc/iotree/.passwd
echo 'user mqttodb' >>/etc/iotree/.acl
echo 'topic read gateways/#' >>/etc/iotree/.acl

# secure files
chmod -R 744 /etc/iotree/config.json
chmod -R 766 /etc/iotree/.acl
chmod -R 766 /etc/iotree/.passwd
chown -R $myvariable:$myvariable /home/$myvariable/dj_iot
chown -R $myvariable:$myvariable /home/$myvariable/iot42
chmod -R 765 /home/$myvariable/dj_iot
chmod 766 /home/$myvariable/dj_iot/db.sqlite3


# setup mosquitto broker user
mosquitto_passwd -b /etc/iotree/.passwd mqttodb $mqttpass

# restart influxdb after config.file changed
systemctl restart influxdb

# making influxdb user: fluxcondj, mqttodb, admin (all privileged),
systemctl start influxdb
sleep 5
# making influxdb user: fluxcondj, mqttodb, admin (all privileged),
curl "http://localhost:8086/query" --data-urlencode "q=CREATE USER admin WITH PASSWORD '$fluxadmin' WITH ALL PRIVILEGES"
curl "http://localhost:8086/query?u=admin&p=$fluxadmin" --data-urlencode "q=CREATE USER fluxcondj WITH PASSWORD '$fluxcondj'"
curl "http://localhost:8086/query?u=admin&p=$fluxadmin" --data-urlencode "q=CREATE USER mqttodb WITH PASSWORD '$fluxmqttodb'"


# start services:
sudo /bin/systemctl daemon-reload
sudo /bin/systemctl enable grafana-server
sudo /bin/systemctl restart grafana-server

systemctl restart influxdb
if [ "$nginx" = true ]; then
systemctl start gunicorn
systemctl enable gunicorn
systemctl reload nginx
fi

if [ "$nginx" = true ]; then
if [ "$full" = true ]; then
ln -s /etc/nginx/sites-available/nginx-ssl-iotree.conf /etc/nginx/sites-enabled/
else
ln -s /etc/nginx/sites-available/nginx-nossl-iotree.conf /etc/nginx/sites-enabled/
fi
rm -r /etc/nginx/sites-enabled/default
systemctl restart nginx
fi

# making grafana user: admin
sleep 10
grafana-cli admin reset-admin-password $grafadmin


## make django and storing script
runuser -u $myvariable -- virtualenv -p python3 /home/$myvariable/iot42/venv1
source /home/$myvariable/iot42/venv1/bin/activate
pip3 install -r /home/$myvariable/iot42/requirements.txt
deactivate

runuser -u $myvariable -- virtualenv -p python3 /home/$myvariable/dj_iot/venv2
source /home/$myvariable/dj_iot/venv2/bin/activate
pip3 install -r /home/$myvariable/dj_iot/requirements.txt
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', '$adminmail', '$djangopass')" | python /home/$myvariable/dj_iot/manage.py shell
python3 /home/$myvariable/dj_iot/manage.py makemigrations
python3 /home/$myvariable/dj_iot/manage.py migrate
python3 /home/$myvariable/dj_iot/manage.py collectstatic
deactivate


if [ "$nginx" = true ]; then
  systemctl restart nginx
  systemctl restart gunicorn
fi


#bugfix for django-revproxy plugin
./bugfix_revproxy.sh '$myvariable'


echo "-Endpoints-		-port-"
echo "grafana:		3000"
echo "influxdb:		8086"
echo "django default:		8080"
if [ "$full" = true ]; then
  echo "mosquitto		8883"
else
  echo "mosquitto		1883"
fi
echo " "
echo "$fluxadmin"
echo "--> Setup complete <--"
echo "--> You might want to check the config.json:"
echo "--> nano /etc/iotree/config.json"
echo "--> You can delete the folder IoTree42"
cd ..

exit

