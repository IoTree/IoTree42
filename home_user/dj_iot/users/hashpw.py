#! Python3

"""
//Iotree42 sensor Network

//purpose: connecting django to pymongo to mongodb, also for checking data and process data for later use
//used software: python3, python module pymongo, json, time, re
//for hardware: Debian-Server

//design by Sebastian Stadler
//on behalf of the university of munich.

//NO WARRANTY AND NO LIABILITY
//use of the code at your own risk.

// This script will hash a given pw so that it will bi acepted from mosquitto
// it also makes a string for entreing in the password file of mosquitto
"""
import base64
import hashlib
import random
import string

class Hashing:
    def __init__(self, username, password):
        self.user=username
        self.pword=password

    def _makeentryline_(self):
        salt_base64 = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
        salt = base64.b64decode(salt_base64)
        to_hash = bytes(self.pword, encoding='utf-8')+salt
        h = hashlib.new("sha512")
        h.update(to_hash)
        hash_base64 = base64.b64encode(h.digest()).decode('ascii')
        hash_pw = "$6$"+salt_base64+"$"+hash_base64
        line_for_file = self.user+":"+hash_pw
        return line_for_file

    def run(self):
        return self._makeentryline_()
