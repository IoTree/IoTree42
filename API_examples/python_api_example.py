import requests
import json
import time

"""
this script will display the last entry of an specific column you define.
you will need to enter the authurl, url, logins, column name, gateway_id, and tree (tree branch)
"""

def main():
    host = ""  # your host adress (ip:port or url)
    username = ""  # login's from web page
    password = ""  # login's from web page
    column = ""  # column name
    gateway_id = ""  # define gateway_id if you have only on gateway leave it empty
    tree_branch = [""]  # define tree branch or sensor-base, list of strings. leave it empty if only one sensor base exists.

    tree = " ".join(tree_branch)
    start_time = (int(time.time())-300)*1000

    auth_url =  str(host)+"/api-token-auth/"  # url to your api-token-auth page
    url = str(host)+'/iotree_api/?format=json'  # url to your iotree api page
    prams = {"username":username, "password":password}
    field_to_process = column
    query = {"gateway_id": gateway_id,
	"tree": tree,
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

if __name__ == '__main__':
    main()
