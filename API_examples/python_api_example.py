import requests
import json
import time

"""
this script will display the last entry of an specific column you define.
you will need to enter the authurl, url, logins, column name, gateway_id, and tree (tree branch)
"""

start_time = (int(time.time())-300)*1000
auth_url = "<your ip or dns>/api-token-auth/"  # url to your api-token-auth page
url = '<your ip or dns>/iotree_api/?format=json'  # url to your iotree api page
prams = {"username":"", "password":""}  # login's from web page
field_to_process = ""  # column name
query = {"gateway_id":"",  # define gateway_id if you have only on gateway leave it empty
	"tree":"",  # define tree branch or sensor-base. leave it empty if only one sensor base exists.
	"filters":"data",
	"in_order":"True", 
	"negated":"False", 
	"time_start":start_time, 
	"time_end":"now"
}

r = requests.post(auth_url, data=prams)
rtoken = r.json().get("token")
token = "Token " + str(rtoken)
headers = {'Authorization': token}
r = requests.post(url, headers=headers, json=query)
json_list = json.loads(r.text)
json_dict = dict(json_list[0])
posts_body = json_dict["posts_body"]
posts_head = json_dict["posts_head"]
print(posts_head)
index = [i for i, s in enumerate(posts_head) if field_to_process in s]
last = posts_body[-1]
last_item = last[index[0]]
print(last_item)
