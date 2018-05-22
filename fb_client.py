
from fbchat import log, Client
from fbchat.models import *
from geeteventbus.subscriber import subscriber
from geeteventbus.eventbus import eventbus
from geeteventbus.event import event

from event_constants import *
from time_event_queuer import *
from message_data import MessageData


import time
import requests
import threading
import random
import datetime
import socket
import subprocess



#class types
ID_TIMER = 0;
ID_LISTENER = 1;

_THREAD_ID = '100001165373491'

# Subclass fbchat.Client and override required methods
class FbClient(threading.Thread,Client,subscriber):
    def __init__(self,eventbus,parser):
        with open('passwd.txt', 'r') as f:
            passwd = [a.strip() for a in f.readlines()]
        threading.Thread.__init__(self)
        Client.__init__(self,passwd[0],passwd[1])
        subscriber.__init__(self)
        
        self.parser = parser
        self.eb = eventbus
        print("Registering Topics")
        self.eb.register_consumer(self,EVENTID_CLIENT_SEND)
        self.eb.register_consumer(self,EVENTID_CLIENT_STOP)
        self.eb.register_consumer(self,EVENTID_CLIENT_START)
        self.eb.register_consumer(self,EVENTID_CLIENT_SNAPSHOT)

    def run(self):
        self.listen()

    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(author_id, thread_id)
        self.markAsRead(author_id)

        #log.info("{} from {} in {}".format(message_object, thread_id, thread_type.name))

        # If Saitama-san is the author -> sayonara
        if author_id == self.uid:
            return
        message_data = MessageData(message_object.text, thread_id, thread_type)
        self.parser.parse(message_data)
        print("Message parsed")

    #Listens on the bus, subscribed to client send, stop and start
    def process(self,new_event):
        print("Event Recieved: {}".format(new_event.get_topic()))
        if not isinstance(new_event,event):
            print("Invalid event type passed")
            return
        if(new_event.get_topic()==EVENTID_CLIENT_SEND):
            self.send_message(new_event)
        elif(new_event.get_topic()==EVENTID_CLIENT_STOP):
            self.stopClient()
        elif(new_event.get_topic()==EVENTID_CLIENT_START):
            self.startClient()
        elif(new_event.get_topic()==EVENTID_CLIENT_SNAPSHOT):
            self.send_snapshot(new_event)

    def startClient(self):
        self.listen()
        print("Exiting Client")

    def stopClient(self):
        print("Stop listneing and logging out")
        self.stopListening()
        self.logout()

    def send_message(self,message_event):
        message_data = message_event.get_data()
        self.send(Message(text=message_data.get_text()),
                thread_id=message_data.get_id(),
                thread_type = message_data.get_type())
    
    def send_snapshot(self,message_event):
        print("Messaging snapshot")
        message_data = message_event.get_data()
        name="newImage"
        img_folder = "captures/"
        subprocess.call(["python2","camera_service.py",img_folder,name])
        img_path = img_folder + name + ".jpg"
        self.sendLocalImage(img_path, message=
                Message(text='This is a local image'),
                thread_id=message_data.get_id(),
                thread_type = message_data.get_type())


    def postIp(self):
        ip = socket.gethostbyname(socket.gethostname())
        print("Sending Ip: " + ip)
        data = MessageData(ip,_THREAD_ID,Thread.USER);
        data.show()
        FbClient.post_message_event(self.eb,message_data);

    @staticmethod
    def post_message_event(eb,message_data):
        print("Posting event")
        eb.post(event(EVENTID_CLIENT_SEND,message_data))



