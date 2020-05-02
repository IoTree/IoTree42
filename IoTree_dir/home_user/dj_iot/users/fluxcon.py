"""
//Iotree42 sensor Network

//purpose: connecting django to pymongo to mongodb, also for checking data and process data for later use
//used software: python3, python module pymongo, json, time, re
//for hardware: Debian-Server

//design by Sebastian Stadler
//on behalf of the university of munich.

//NO WARRANTY AND NO LIABILITY
//use of the code at your own risk.
"""


from influxdb import InfluxDBClient
import json


with open('/etc/iotree/config.json', encoding='utf-8') as config_file:
   config = json.load(config_file)

client = InfluxDBClient(host=config['FLUX_ADRESS'], port=int(config['FLUX_PORT']), username=config['FLUX_USER'], password=config['FLUX_PW'])

class InitInfluxUser:
    def __init__(self, user, pword):
        self.user = user
        self.pword = pword

    def run(self):
        try:
            client.create_user(self.user, self.pword, admin=False)
            client.create_database(self.user)
            client.grant_privilege('read', self.user, self.user)
            client.grant_privilege('write', self.user, config['MQTTOFLUX_USER'])
            client.grant_privilege('read', self.user, config['FLUX_DJANGO_USER'])
            return self.user
        except RuntimeError:
            return False


class DelInfluxAll:
    def __init__(self, user):
        self.user = user

    def run(self):
        try:
            client.revoke_privilege('all', self.user, self.user)
            client.revoke_privilege('all', self.user, config['MQTTOFLUX_USER'])
            client.revoke_privilege('all', self.user, config['FLUX_DJANGO_USER'])
            client.drop_database(self.user)
            client.drop_user(self.user)
            return self.user
        except RuntimeError:
            return False


class DelInfluxData:
    def __init__(self, user, giventags):
        self.user = user
        self.giventags = giventags

    def run(self):
        try:
            for n in self.giventags:
                client.switch_database(self.user)
                client.drop_measurement(n)
            return self.user
        except RuntimeError:
            return False

