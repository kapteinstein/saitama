


from fbchat import log, Client
from fbchat.models import *
from geeteventbus.subscriber import subscriber
from geeteventbus.eventbus import eventbus
from geeteventbus.event import event

from time_event_queuer import *
from message_parser import *
from fb_client import *
from event_constants import *
from internet_status import InternetStatus
from weather_forcast import WeatherForcast


import time
import requests
import threading
import random
import datetime



def main():
    eb = eventbus()
    parser = MessageParser(eb)

    cv = threading.Condition() #conditional Variable
    teq = TimeEventQueuer(eb,cv)
    teq.start()

    internet_check = InternetStatus(eb)
    weather_forcast = WeatherForcast(eb)

    client = FbClient(eb,parser)
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
