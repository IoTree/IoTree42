##! Python3

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


import json
import requests

with open('/etc/iotree/config.json', encoding='utf-8') as config_file:
   config = json.load(config_file)


class InitGrafaUser:
    def __init__(self, username, password, email):
        self.user=username
        self.pword=password
        self.email=email

    def _makeorg_(self):
        payload = '{"name": "'
        payload += self.user
        payload += '"}'
        url = "http://{}:{}@{}:{}/api/orgs".format(config['GRAFA_USER'], config['GRAFA_PW'], config['GRAFA_ADRESS'], config['GRAFA_PORT'])
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=payload, headers=headers)
        return r

    def _getorgid_(self):
        url = "http://{}:{}@{}:{}/api/orgs/name/{}".format(config['GRAFA_USER'], config['GRAFA_PW'], config['GRAFA_ADRESS'], config['GRAFA_PORT'], self.user)
        headers = {'content-type': 'application/json'}
        r = requests.get(url, headers=headers)
        content = json.loads(r.text)
        orgid = content["id"]
        return orgid

    def _switchorg_(self, orgid):
        url = "http://{}:{}@{}:{}/api/user/using/{}".format(config['GRAFA_USER'], config['GRAFA_PW'], config['GRAFA_ADRESS'], config['GRAFA_PORT'], orgid)
        headers = {'content-type': 'application/json'}
        r = requests.post(url, headers=headers)
        return r

    def _makeuser_(self):
        payload = '{"name":"'
        payload += self.user
        payload += '", "email":"'
        payload += self.email
        payload += '", "login":"'
        payload += self.user
        payload += '", "password":"'
        payload += self.pword
        payload += '"}'
        headers = {'content-type': 'application/json'}
        url = "http://{}:{}@{}:{}/api/admin/users".format(config['GRAFA_USER'], config['GRAFA_PW'], config['GRAFA_ADRESS'], config['GRAFA_PORT'])
        r = requests.post(url, data=payload, headers=headers)
        return r

    def _addusertoorg_(self, orgid):
        payload = '{"role":"Editor", "loginOrEmail": "'
        payload += self.user
        payload += '"}'
        url = "http://{}:{}@{}:{}/api/orgs/{}/users".format(config['GRAFA_USER'], config['GRAFA_PW'], config['GRAFA_ADRESS'], config['GRAFA_PORT'], orgid)
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=payload, headers=headers)
        return r

    def _makesou_(self):
        payload = '{"access": "proxy", '
        payload += '"database":"'
        payload += self.user
        payload += '", "name":"'
        payload += self.user
        payload += '", "type":"influxdb", '
        payload += '"url": "http://{}:{}", '.format(config['FLUX_ADRESS'], config['FLUX_PORT'])
        payload += '"user":"'
        payload += self.user
        payload += '", "password":"'
        payload += self.pword
        payload += '", "basicAuth": true, "basicAuthUser": "'
        payload += self.user
        payload += '", "secureJsonData": {"basicAuthPassword": "'
        payload += self.pword
        payload += '"}, "jsonData":{"httpMode": "GET"}'
        payload += ', "isDefault":true}'
        headers = {'content-type': 'application/json'}
        url = "http://{}:{}@{}:{}/api/datasources".format(config['GRAFA_USER'], config['GRAFA_PW'], config['GRAFA_ADRESS'], config['GRAFA_PORT'])
        r = requests.post(url, data=payload, headers=headers)
        return r

    def _getuserid_(self):
        url = "http://{}:{}@{}:{}/api/users/lookup?loginOrEmail={}".format(config['GRAFA_USER'], config['GRAFA_PW'], config['GRAFA_ADRESS'], config['GRAFA_PORT'], self.user)
        headers = {'content-type': 'application/json'}
        r = requests.get(url, headers=headers)
        content = json.loads(r.text)
        userid = content["id"]
        return userid

    def _switchuserorg_(self, userid, orgid):
        url = "http://{}:{}@{}:{}/api/users/{}/using/{}".format(config['GRAFA_USER'], config['GRAFA_PW'], config['GRAFA_ADRESS'], config['GRAFA_PORT'], userid, orgid)
        headers = {'content-type': 'application/json'}
        r = requests.post(url,  headers=headers)
        return r

    def _switchorgmain_(self):
        url = "http://{}:{}@{}:{}/api/user/using/1".format(config['GRAFA_USER'], config['GRAFA_PW'], config['GRAFA_ADRESS'], config['GRAFA_PORT'])
        headers = {'content-type': 'application/json'}
        r = requests.post(url, headers=headers)
        return r

    def run(self):
        try:
            self._makeorg_()
            orgid = self._getorgid_()
            self._switchorg_(orgid)
            self._makeuser_()
            self._addusertoorg_(orgid)
            self._makesou_()
            userid = self._getuserid_()
            self._switchuserorg_(userid, orgid)
            self._switchorgmain_()
            return True
        except FileExistsError:
            return False

class DelGrafaAll:
    def __init__(self, username):
        self.user = username

    def _getuserid_(self):
        url = "http://{}:{}@{}:{}/api/users/lookup?loginOrEmail={}".format(config['GRAFA_USER'], config['GRAFA_PW'], config['GRAFA_ADRESS'], config['GRAFA_PORT'], self.user)
        headers = {'content-type': 'application/json'}
        r = requests.get(url, headers=headers)
        content = json.loads(r.text)
        userid = content["id"]
        return userid

    def _deluser_(self, userid):
        headers = {'content-type': 'application/json'}
        url = "http://{}:{}@{}:{}/api/admin/users/{}".format(config['GRAFA_USER'], config['GRAFA_PW'], config['GRAFA_ADRESS'], config['GRAFA_PORT'], userid)
        r = requests.delete(url, headers=headers)
        return r

    def _getorgid_(self):
        url = "http://{}:{}@{}:{}/api/orgs/name/{}".format(config['GRAFA_USER'], config['GRAFA_PW'], config['GRAFA_ADRESS'], config['GRAFA_PORT'], self.user)
        headers = {'content-type': 'application/json'}
        r = requests.get(url, headers=headers)
        content = json.loads(r.text)
        orgid = content["id"]
        print(orgid)
        return orgid

    def _delorg_(self, orgid):
        headers = {'content-type': 'application/json'}
        url = "http://{}:{}@{}:{}/api/orgs/{}".format(config['GRAFA_USER'], config['GRAFA_PW'], config['GRAFA_ADRESS'], config['GRAFA_PORT'], orgid)
        r = requests.delete(url, headers=headers)
        print(r)
        return r

    def _switchorgmain_(self):
        url = "http://{}:{}@{}:{}/api/user/using/1".format(config['GRAFA_USER'], config['GRAFA_PW'], config['GRAFA_ADRESS'], config['GRAFA_PORT'])
        headers = {'content-type': 'application/json'}
        r = requests.post(url, headers=headers)
        return r

    def run(self):
        try:
            userid = self._getuserid_()
            self._deluser_(userid)
            orgid = self._getorgid_()
            self._delorg_(orgid)
            self._switchorgmain_()
            return True
        except FileExistsError:
            return False

