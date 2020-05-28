import requests
import json
import time

"""
this script will display the last entry of your saved Datasets/Measurement
also it will display the last entry of an specific column if you define.
"""

def main():
    #host = ""  # your host adress (ip:port or url)
    #username = ""  # login's from web page
    #password = ""  # login's from web page
    host = input("your host adress (ip:port or url): \n")
    username = input("Your username login's from web page: \n")
    password = input("Your password login's from web page: \n")
    column = ""
    interval = 300 # Time interval until now in which data is searched. Take your measurementinterall and multiply it by 2

    start_time = int(time.time())-interval

    auth_url =  str(host)+"/api-token-auth/"  # url to your api-token-auth page
    url = str(host)+'/iotree_api/?format=json'  # url to your iotree api page
    prams = {"username":username, "password":password}
    field_to_process = column

    r = requests.post(auth_url, data=prams)
    rtoken = r.json().get("token")
    token = "Token " + str(rtoken)
    headers = {'Authorization': token}
    r = requests.get(url, headers=headers)
    treeids = json.loads(r.json())
    listofleefs = []
    for n in treeids:
        for m in n["children"]:
            listofleefs.append(m["id"])
    print(listofleefs)
    tree = input("Choose one or more of your noodes or leefs and enter it separated through ",": \n")
    query = {
        "tree": tree,
        "time_start":start_time,
        "time_end":"now"
         }
    r = requests.post(url, headers=headers, json=query)
    json_list = json.loads(r.text)
    coun = 1
    for n in json_list:
        try:
                json_dict = dict(n)
                posts_body = json_dict["posts_body"]
                posts_head = json_dict["posts_head"]
                index = [i for i, s in enumerate(posts_head) if field_to_process in s]
                last = posts_body[-1]
                strn =""
                counter = 0
                for n in posts_head:
                    strn+=str(n)+" = "+str(last[counter])+", "
                    counter += 1
                print(str(coun)+". hole last entry: "+strn)
                #print(posts_head) print(str(last))
                last_item = last[index[0]]
                print(str(coun)+". specific column: "+str(column)+": "+str(last_item))
        except:
                print(str(coun)+". no data found under this branch")
        coun+=1

if __name__ == '__main__':
    main()

   "time_start":start_time,
        "time_end":"now"
