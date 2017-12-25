


from geeteventbus.subscriber import subscriber
from geeteventbus.eventbus import eventbus
from geeteventbus.event import event

from fbchat.models import *
import threading
import requests
import datetime

from event_constants import *
from time_event_queuer import *
from message_data import MessageData
from repeating_event_object import RepeatingEventObject

_BASE_URL = 'http://spaghettiprojecti.no/saitama/'
_THREAD_ID = '1434497743266652'

class InternetStatus(threading.Thread, subscriber):
    def __init__(self, eb):
        super().__init__()
        self.previous = "Internet Status: Det er ikke registrert noen problemer i ditt område."
        self.eb = eb
        self.eb.register_consumer(self, EVENTID_INTERNET_CHECK)
        self.msg_data = MessageData('', thread_id=_THREAD_ID,
                thread_type=ThreadType.GROUP)
        self.repeating_event = RepeatingEventObject(eb,
                event(EVENTID_INTERNET_CHECK, None), datetime.now(),
                timedelta(minutes = 4))
        self.repeating_event.queue()
        print("internet status init")

    def process(self,new_event):
        # print("Event Recieved: {}".format(new_event.get_topic()))
        if not isinstance(new_event, event):
            print("Invalid event type passed")
            return
        if(new_event.get_topic() == EVENTID_INTERNET_CHECK):
            self.get_status()

    def get_status(self):
        url = "https://kabel.canaldigital.no/hjelp/sok-etter-feil/?facebook=False&q=7033"
        a = requests.get(url)

        start_str = "class=\"searchresultItem\">"
        end_str = "</h2>"
        start = a.text.find(start_str)
        end = a.text.find(end_str, start)

        s = a.text[start+len(start_str):end]
        s = s.replace("<h2>", "")
        s = s.replace("&#229;", "å")  # superhacky. klarer ikke fikse utf-8
        s = s.strip()
        s = "Internet Status: " + s

        # print("post internet status")
        if s != self.previous:
            self.previous = s
            self.msg_data.set_text(s)
            Fb_client.post_message_event(self.eb, self.msg_data)

