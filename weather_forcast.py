# -*- coding: utf-8 -*-
from geeteventbus.subscriber import subscriber
from geeteventbus.eventbus import eventbus
from geeteventbus.event import event
from fbchat.models import *


import threading
import requests
import datetime
import sys

from event_constants import *
from message_data import MessageData
from repeating_event_object import RepeatingEventObject
_THREAD_ID = '1434497743266652'
_URL_TRONDHEIM = "https://www.yr.no/place/Norway/S%C3%B8r-Tr%C3%B8ndelag/Trondheim/Trondheim/"
_URL_OSLO = "https://www.yr.no/place/Norway/Oslo/Oslo/Oslo/"
class WeatherForcast(threading.Thread,subscriber):
    def __init__(self, eb):
        super().__init__()
        self.eb = eb
        self.eb.register_consumer(self, EVENTID_WEATHER_CHECK)
        self.eb.register_consumer(self, EVENTID_WEATHER_SUBSCRIPTION)
        self.msg_data = MessageData('', thread_id=_THREAD_ID,
                thread_type=ThreadType.GROUP)
        print("Weather Module status Init")


    def process(self,new_event):
        # print("Event Recieved: {}".format(new_event.get_topic()))
        if not isinstance(new_event, event):
            print("Invalid event type passed")
            return
        if(new_event.get_topic() == EVENTID_WEATHER_CHECK):
            msg_data = new_event.get_data()
            msg_data.set_text(self.get_weather())
            self.eb.post(event(EVENTID_CLIENT_SEND,msg_data))
        if(new_event.get_topic() == EVENTID_WEATHER_SUBSCRIPTION):
            self.handle_subscription(new_event)

    def get_weather(self):
        content = requests.get(_URL_TRONDHEIM)
          
        table_class = "class=\"yr-table yr-table-overview2 yr-popup-area\""
        table_start = content.text.find(table_class)
        table_end = content.text.find(table_class,table_start+1)
        table_content = content.text[table_start:table_end]

        body_tag = "<tbody>" 
        body_start = table_content.find(body_tag)
        body_end = table_content.find("</tbody>",body_start+1)
        body_content = table_content[body_start:body_end]

        row_end = 0
        weather = "Weather Forecast Trondheim " + datetime.date.today().isoformat() + "\n"
        while(True):
            row_tag = "<tr>"
            row_start = body_content.find(row_tag,row_end)
            row_end = body_content.find("</tr>",row_start+1)
            if(row_start < 0 or row_end < 0): break
            row_content = body_content[row_start:row_end]
            
            td_end = 0
            row_array = row_content.split("<td")
            time = self.get_time(row_array[1])
            temp = self.get_temp(row_array[3])
            rain  = self.get_rain(row_array[4])
            wind  = self.get_wind(row_array[5])
            weather += time + " \t " + temp + " \t " + rain + "\t " + wind + "\n"
        return weather

    def get_time(self,t):
        t_s = t.find(">")
        t_e = t.find("<")
        s = t[t_s+2:t_e].encode(sys.stdout.encoding, errors="replace").decode("utf8")
        s = s.replace("?","-")
        return s
    
    def get_temp(self,t):
        t_s = t.find(">")
        t_e = t.find("<")
        s = t[t_s+1:t_e]
        return s
    
    def get_rain(self,t):
        t_s = t.find(">")
        t_e = t.find("<")
        s = t[t_s+1:t_e].encode(sys.stdout.encoding, errors="replace").decode("utf8")
        s = s.replace("?","-")
        return s

    def get_wind(self,t):
        i_s = t.find("<img")
        t_s = t.find(">",i_s)
        t_e = t.find("<",t_s)
        s = t[t_s+1:t_e].encode(sys.stdout.encoding, errors="replace").decode("utf8")
        a = s.split()
        for i in range(len(a)):
            if(a[i].isdigit()):
                return a[i] + " m/s"

    def handle_subscription(self,subscription_event):
        sub = subscription_event.get_data()
        occ = sub.get_occurrence()
        interval = sub.get_interval()
        msg_data = sub.get_data()
        weather_event = event(EVENTID_WEATHER_CHECK,msg_data)
        rep_event = RepeatingEventObject(self.eb,weather_event,occ,interval,7)
        rep_event.queue()
        print("RepeatingEvent has been queued")





        
    def encode_print(self,text):
        print(text.encode(sys.stdout.encoding, errors='replace'))
           
if __name__ == "__main__": 
    eb = eventbus()
    wf = WeatherForcast(eb)
    print(wf.get_weather())

    eb.shutdown()


