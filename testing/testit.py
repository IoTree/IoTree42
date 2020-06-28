#! c:\python34\python3
#!/usr/bin/env python
#modivide form::::
##demo code provided by Steve Cope at www.steves-internet-guide.com
##email steve@steves-internet-guide.com
##Free to use for any purpose
##If you like and use this code you can
##buy me a drink here https://www.paypal.me/StepenCope
"""
Creates multiple Connections to a broker 
and sends and receives messages.
Uses one thread per client
-> add clients e.g. by copy past do open more threads -> more load on target
"""
import paho.mqtt.client as mqtt
import time
import json
import threading
import logging

logging.basicConfig(level=logging.INFO)



clients=[
{"broker":"<ip of brocker>","port":8883,"cafile":"<path to cafile>","name":"<username>","password":"<user pw>","sub_topic":"gateways/tester2/gateway1/test1","pub_topic":"gateways/tester2/gateway1/test1"},
]


nclients=len(clients)
#message={}

def Connect(client,broker,port,keepalive,run_forever=False):
    """Attempts connection set delay to >1 to keep trying
    but at longer intervals. If runforever flag is true then
    it will keep trying to connect or reconnect indefinetly otherwise
    gives up after 3 failed attempts"""
    connflag=False
    delay=5
    #print("connecting ",client)
    badcount=0 # counter for bad connection attempts
    while not connflag:
        logging.info("connecting to broker "+str(broker))
        #print("connecting to broker "+str(broker)+":"+str(port))
        print("Attempts ",str(badcount))
        time.sleep(delay)
        try:
            client.connect(broker,port,keepalive)
            connflag=True

        except:
            client.badconnection_flag=True
            logging.info("connection failed "+str(badcount))
            badcount +=1
            if badcount>=3 and not run_forever: 
                return -1
                raise SystemExit #give up


                
    return 0
    #####end connecting
def wait_for(client,msgType,period=1,wait_time=10,running_loop=False):
    """Will wait for a particular event gives up after period*wait_time, Default=10
seconds.Returns True if succesful False if fails"""
    #running loop is true when using loop_start or loop_forever
    client.running_loop=running_loop #
    wcount=0  
    while True:
        logging.info("waiting"+ msgType)
        if msgType=="CONNACK":
            if client.on_connect:
                if client.connected_flag:
                    return True
                if client.bad_connection_flag: #
                    return False
                
        if msgType=="SUBACK":
            if client.on_subscribe:
                if client.suback_flag:
                    return True
        if msgType=="MESSAGE":
            if client.on_message:
                if client.message_received_flag:
                    return True
        if msgType=="PUBACK":
            if client.on_publish:        
                if client.puback_flag:
                    return True
     
        if not client.running_loop:
            client.loop(.01)  #check for messages manually
        time.sleep(period)
        wcount+=1
        if wcount>wait_time:
            print("return from wait loop taken too long")
            return False
    return True

def client_loop(client,broker,port,pub_topic,client_id,keepalive=60,loop_function=None,\
             loop_delay=1,run_forever=False):
    """runs a loop that will auto reconnect and subscribe to topics
    pass topics as a list of tuples. You can pass a function to be
    called at set intervals determined by the loop_delay
    """
    client.run_flag=True
    client.broker=broker
    print("running loop ")
    client.reconnect_delay_set(min_delay=1, max_delay=12)
    message={}
    number=1
    while client.run_flag: #loop forever
        message["id"]=client_id+str(number)
        message["timestemp"]=time.time()

        if client.bad_connection_flag:
            break
        if not client.connected_flag:
            print("Connecting to ",broker)
            if Connect(client,broker,port,keepalive,run_forever) !=-1:
                if not wait_for(client,"CONNACK"):
                   client.run_flag=False #break no connack
            else:#connect fails
                client.run_flag=False #break
                print("quitting loop for  broker ",broker)

        client.loop(0.01)

        if client.connected_flag and loop_function: #function to call
                loop_function(client,loop_delay, pub_topic, json.dumps(message)) #call function
                number=number+1
    time.sleep(1)
    print("disconnecting from",broker)
    if client.connected_flag:
        client.disconnect()
        client.connected_flag=False
    
def on_log(client, userdata, level, buf):
   print(buf)
def on_message(client, userdata, message):
#   time.sleep(1)
   print("message received",str(message.payload.decode("utf-8")))
def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        for c in clients:
          if client==c["client"]:
              if c["sub_topic"]!="":
                  client.subscribe(c["sub_topic"])
          
        #print("connected OK")
    else:
        print("Bad connection Returned code=",rc)
        client.loop_stop()  
def on_disconnect(client, userdata, rc):
   client.connected_flag=False #set flag
   #print("client disconnected ok")
def on_publish(client, userdata, mid):
   time.sleep(1)
   print("In on_pub callback mid= "  ,mid)

def pub(client,loop_delay, pub_topic, message_send):
    #print("in publish")
    client.publish(pub_topic, message_send, qos=2)
#    time.sleep(loop_delay)
    pass

def Create_connections():
   for i in range(nclients):
      broker=clients[i]["broker"]
      port=clients[i]["port"]
      name=clients[i]["name"]
      password=clients[i]["password"]
      cafile=clients[i]["cafile"]
      pub_topic=clients[i]["pub_topic"]
      cname="client"+str(i)+"_"
      t=int(time.time())
      client_id =cname+str(t)+"_"+name+"_" #create unique client_id
      client = mqtt.Client(client_id)             #create new instance
      clients[i]["client"]=client 
      clients[i]["client_id"]=client_id
      clients[i]["cname"]=cname
      client.on_connect = on_connect
      client.on_disconnect = on_disconnect
      #client.on_publish = on_publish
      client.on_message = on_message
      client.tls_set(cafile)
      client.username_pw_set(username=name,password=password)
      t = threading.Thread(target\
            =client_loop,args=(client,broker,port,pub_topic,client_id,60,pub))
      threads.append(t)
      t.start()


mqtt.Client.connected_flag=False #create flag in class
mqtt.Client.bad_connection_flag=False #create flag in class

threads=[]
print("Creating Connections ")
no_threads=threading.active_count()
print("current threads =",no_threads)
print("Publishing ")
Create_connections()

print("All clients connected ")
no_threads=threading.active_count()
print("current threads =",no_threads)
print("starting main loop")
try:
    while True:
        time.sleep(10)
        no_threads=threading.active_count()
        print("current threads =",no_threads)
        for c in clients:
            if not c["client"].connected_flag:
                print("broker ",c["broker"]," is disconnected")
    

except KeyboardInterrupt:
    print("ending")
    for c in clients:
        c["client"].run_flag=False
time.sleep(10)
   
