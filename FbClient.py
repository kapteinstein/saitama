from fbchat import log, Client
from fbchat.models import *
from geeteventbus.subscriber import subscriber
from geeteventbus.eventbus import eventbus
from geeteventbus.event import event
from timeEventQueuer import *
from Message_parser import *

import time
import requests
import threading
import random
import datetime

#class types
ID_TIMER = 0;
ID_LISTENER = 1;
EVENTID_CLIENT_SEND = "Topic Message Send"
EVENTID_CLIENT_STOP = "Topic Stop Client"
EVENTID_CLIENT_START = "Topic Start Client"

_BASE_URL = 'http://spaghettiprojecti.no/saitama/'
_THREAD_ID = '1434497743266652'

# Subclass fbchat.Client and override required methods
class Fb_client(threading.Thread,Client,subscriber):
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
    def run(self):
        self.listen()

    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(author_id, thread_id)
        self.markAsRead(author_id)

        #log.info("{} from {} in {}".format(message_object, thread_id, thread_type.name))

        # If Saitama-san is the author -> sayonara
        if author_id == self.uid:
            return
       
        message_data = Message_data(message_object.text, thread_id, thread_type)
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

    @staticmethod
    def post_message_event(eb,message_data):
        print("Posting event")
        eb.post(event(EVENTID_CLIENT_SEND,message_data))

class Message_data():
    def __init__(self,text,thread_id,thread_type):
        self.text = text
        self.thread_id = thread_id
        self.thread_type = thread_type

    def get_text(self): return self.text
    def set_text(self,text): self.text = text
    def get_id(self,): return self.thread_id
    def get_type(self,): return self.thread_type

        

        

    
def main():
    eb = eventbus()
    parser = Message_parser(eb)

    cv = threading.Condition() #conditional Variable
    teq = Time_event_queuer(eb,cv)
    teq.start()


    client = Fb_client(eb,parser)
    client.start()
    #eb.post(event(EVENTID_CLIENT_START,""))
    """
    print("Joining")
    while(client.isAlive()):
        time.sleep(1)
    client.join() 
    """
    client.join()
    print ("Exiting Main Thread")
    eb.post(event(EVENTID_QUEUE_STOP,""))
    teq.join()
    eb.shutdown()


if __name__ == "__main__":
    main()