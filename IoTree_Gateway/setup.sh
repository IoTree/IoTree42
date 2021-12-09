#!/bin/bash


echo "******************************************"
echo "*  _____   _______            _  _ ___   *"
echo "* |_   _| |__   __|          | || |__ \  *"
echo "*   | |  ___ | |_ __ ___  ___| || |_ ) | *"
echo "*   | | / _ \| | '__/ _ \/ _ \__   _/ /  *"
echo "*  _| || (_) | | | |  __/  __/  | |/ /_  *"
echo "* |_____\___/|_|_|  \___|\___|  |_|____| *"
echo "*                                        *"
echo "******************************************"
echo "<<<-----         Credentials         --->>>"
echo "ENTER your MQTT-Username is the same as on the Web-Site"
read Username
echo "<<<-----      Broker IP/Hostname     --->>>"
echo "ENTER MQTT-Broker IP or Hostname"
read Hostname
echo "<<<-----         Broker Port         --->>>"
echo "ENTER MQTT-Broker Port. In general 1883 or 8883 for TLS"
read Port
echo "<<<--          MQTT-Password          -->>>"
echo "ENTER your MQTT-Password same as on the Web-Site. !HIDDEN INPUT!"
read -s Password
echo "<<<--             Gateway-ID          -->>>"
echo "DEFINE a Gateway-ID (only alphanumeric!):"
read GatewayID
if [ -n "$(tr -d '[:alnum:]' <<<$GatewayID)" ]
then
    echo "Invalid input ONLY alphanumeric! Please try again."
    exit 1
else
    echo valid
fi

NEW_UUID=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 8 | head -n 1)

sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y install mosquitto
sudo apt-get -y install mosquitto-clients
sudo apt-get -y install inotify-tools

if test -f "/etc/mosquitto/mosquitto.conf.iotree_save"; then
    rm -r /etc/mosquitto/mosquitto.conf
else
    mv /etc/mosquitto/mosquitto.conf /etc/mosquitto/mosquitto.conf.iotree_save
fi

echo 'port 1883' >>/etc/mosquitto/mosquitto.conf
echo 'allow_anonymous true' >>/etc/mosquitto/mosquitto.conf
string="connection ${GatewayID}"
echo ${string} >>/etc/mosquitto/mosquitto.conf
echo 'cleansession false' >>/etc/mosquitto/mosquitto.conf
string="address ${Hostname}:${Port}"
echo ${string} >>/etc/mosquitto/mosquitto.conf
string="remote_password ${Password}"
echo ${string} >>/etc/mosquitto/mosquitto.conf
string="remote_username ${Username}"
echo ${string} >>/etc/mosquitto/mosquitto.conf
if [ "$Port" = "8883"]; then
   echo 'bridge_cafile /etc/mosquitto/certs/DST_Root_CA_X3.pem' >>/etc/mosquitto/mosquitto.conf
fi
string="remote_clientid ${GatewayID}${NEW_UUID}"
echo ${string} >>/etc/mosquitto/mosquitto.conf
string="topic # both 2 universe/ gateways/${Username}/${GatewayID}/"
echo ${string} >>/etc/mosquitto/mosquitto.conf

chmod -R 644 /etc/mosquitto/mosquitto.conf

if [ "$Port" = "8883"]; then
   cp -r ./DST_Root_CA_X3.pem /etc/mosquitto/certs/DST_Root_CA_X3.pem
fi

rm -r /etc/giotree
cp -r ./giotree /etc/giotree


echo $Username >/etc/giotree/CredentialsFile.txt
echo $Password >>/etc/giotree/CredentialsFile.txt
echo $GatewayID >>/etc/giotree/CredentialsFile.txt
echo $Hostname >>/etc/giotree/CredentialsFile.txt
echo $Port >>/etc/giotree/CredentialsFile.txt

chmod 777 /etc/giotree/SyncFile.json

username=$(whoami)
crontab -r


line="* * * * * mosquitto_pub -t universe/SYSTEMcontrol/ping -m '{\"notimestamp\":true}' -h localhost -p 1883"
(crontab -u $username -l; echo "$line" ) | crontab -u $username -


echo "<<<-----     Send Command Func.    ----->>>"
echo "Do you want command send to be enabled (yes/no)"
read commandsend
if [ "$commandsend" == "yes" ]
then
    line="@reboot bash /etc/giotree/CommandSUB.sh"
    (crontab -u $username -l; echo "$line" ) | crontab -u $username -
    bash /etc/giotree/CommandSUB.sh&
elif [ "$commandsend" == "no" ]
then
    echo "you can still activate this function by adding this line to crontab:"
    echo "@reboot bash /etc/giotree/CommandSUB.sh"
else
    echo "please enter 'yes' or 'no'"
    exit
fi


echo "<<<-----       Json File Func.     ----->>>"
echo "Do you want Json File to be enabled (yes/no)"
read jsonfile
if [ "$jsonfile" == "yes" ]
then
    line="@reboot bash /etc/giotree/FileSUB.sh"
    (crontab -u $username -l; echo "$line" ) | crontab -u $username -
    line="@reboot bash /etc/giotree/FileSync.sh"
    (crontab -u $username -l; echo "$line" ) | crontab -u $username -
    bash /etc/giotree/FileSUB.sh&
    bash /etc/giotree/FileSync.sh&
elif [ "$jsonfile" == "no" ]
then
    echo "you can still activate this function by adding this lines to crontab:"
    echo "@reboot bash /etc/giotree/FileSUB.sh"
    echo "and"
    echo "@reboot bash /etc/giotree/FileSync.sh"
else
    echo "please enter 'yes' or 'no'"
    exit
fi

sleep 0.5

echo "<<<-----     Link Gateway Func.    ----->>>"
echo "Do you want your gateway link to another gateway (yes/no)"
read linkgateway
if [ "$linkgateway" == "yes" ]
then
    line="@reboot bash /etc/giotree/LinkGateways.sh"
    (crontab -u $username -l; echo "$line" ) | crontab -u $username -
    bash /etc/giotree/LinkGateways.sh&
elif [ "$linkgateway" == "no" ]
then
    echo "you can still activate this function by adding this line to crontab:"
    echo "@reboot bash /etc/giotree/LinkGateways.sh"
else
    echo "please enter 'yes' or 'no'"
    exit
fi

sleep 1
sudo systemctl restart mosquitto
sleep 1

echo "Everything is setup please check if heartbeat can be seen on the Iotree42 Platform."
echo "If necessary check with 'sudo systemctl status mosquitto' if Broker isn't running properly."
echo "And Please:"
echo "<<<<      PLEASE REBOOT!      >>>>"
