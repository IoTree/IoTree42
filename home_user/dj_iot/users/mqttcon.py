#!pyton3
"""
Workaourond for setting up an mosquttion user and the related acl's
bash script in background takes care of hashing and reloading the mosquitto broker
"""

from django.contrib.auth.models import User
import subprocess
import json
from .hashpw import Hashing

with open('/etc/iotree/config.json', encoding='utf-8') as config_file:
   config = json.load(config_file)


# saves user to acl and hashing file
class InitMqttClient:
    def __init__(self, user, pword):
        self.user = user
        self.pword = pword

    def run(self):
        try:
            f = open(config['MQTT_ACL_PATH'], "a")
            f.write(
                "\nuser " + str(self.user) + "\ntopic readwrite gateways/" + str(self.user) + "/#")
            f.close()
            # make user-pass entry into password file after
            hashing_client = Hashing(self.user, self.pword)
            line_for_file = hashing_client.run()
            f = open(config['MQTT_PASS_PATH'], "a")
            f.write(
                "\n"+line_for_file)
            f.close()
            return True
        except RuntimeError:
            return False


# delete user form acl and passwd file
class DelMqttClient:
    def __init__(self, user):
        self.user = user

    def deldel(self):
        try:
            linedel1 = "user " + str(self.user)
            linedel2 = "/" + str(self.user) + "/"
            with open(config['MQTT_ACL_PATH'], "r") as f:
                lines = f.readlines()
            with open(config['MQTT_ACL_PATH'], "w") as f:
                for line in lines:
                    if linedel1 not in line.strip("\n"):
                        f.write(line)
            f.close()
            with open(config['MQTT_ACL_PATH'], "r") as b:
                lines1 = b.readlines()
            with open(config['MQTT_ACL_PATH'], "w") as b:
                for line in lines1:
                    if linedel2 not in line.strip("\n"):
                        b.write(line)
            b.close()
            linedel1 = None
            linedel2 = None
            # deleting user from mosquitto user file
            linedel3 = str(self.user)+":"
            with open(config['MQTT_PASS_PATH'], "r") as c:
                lines2 = c.readlines()
            with open(config['MQTT_PASS_PATH'], "w") as c:
                for line in lines2:
                    if linedel3 not in line.strip("\n"):
                        c.write(line)
            linedel3 = None
            return True
        except RuntimeError:
            return False

