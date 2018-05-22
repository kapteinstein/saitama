from geeteventbus.event import event
from datetime import datetime, timedelta,date

from subscription import Subscription
from message_data import MessageData

from fb_client import *
from event_constants import *
from time import sleep

TIME_KEYES = ['d','h','m','s']
help_path = "help.txt"
class MessageParser():
    def __init__(self,event_bus):
        self.eb = event_bus

    def parse(self,message_data):
        text = message_data.get_text()
        print(text)
        print(message_data.get_id())
        # echo if message start with @echo
        if text.startswith('!echo'):
            print("Echoing")
            message_data.set_text(text[6::])
            FbClient.post_message_event(self.eb,message_data)
            return

        # send dad joke if message start with @dad

        if '!logout' in text:
            message_data.set_text("Logging out")
            FbClient.post_message_event(self.eb,message_data)
            sleep(1)
            print("Posting Stop event")
            self.eb.post(event(EVENTID_CLIENT_STOP,""))

        elif text.startswith('!rm'):
            self.parseRemindMe(message_data)

        elif text.startswith('!help'):
            self.parseHelp(message_data)

        elif text.startswith('!repeat'):
            self.parseRepeat(message_data)
        
        elif text.startswith('!weather'):
            self.parseWeather(message_data)
            
        elif text.startswith('!sub'):
            self.parseSubscription(message_data)

        elif text.startswith('!ip'):
            self.parseIp(message_data)

        elif text.startswith('!capture'):
            self.parse_snapshot(message_data)

        elif '!dad' in text:
            print("Dading")
            joke = requests.get('https://icanhazdadjoke.com/',
                    headers={'Accept': 'text/plain'})
            joke.encoding = 'utf-8'
            message_data.set_text(joke.text)
            FbClient.post_message_event(self.eb,message_data)
            return

        elif text.startswith("!"):
            message_data.set_text(message_data.text + " is yet to be implemented")
            FbClient.post_message_event(self.eb,message_data)

    #Returns timedelta object from text on format ?w?d?h?m?s
    def get_time_delta_from_text(self,text):
        time_delta = timedelta(seconds=0)
        number = "0"
        for c in text:
            if(c.isdigit()):
                number += c
            elif(c in TIME_KEYES):
                time_delta += self.get_character_time(number,c)
                number = "0"
        return time_delta

    def get_time_from_text(self,text):
        a = text.split()
        print(a)
        for s in a:
            if s.startswith("@"):
                print(s)
                td = self.get_time_delta_from_text(s[1:])
                print(td)
                t = (datetime.datetime.min + td).time()
                d = datetime.date.today()
                dt = datetime.datetime.combine(d,t)
                if(datetime.datetime.now() > dt):
                    dt = dt.replace(day = d.day + 1)
                return dt
        return datetime.datetime.now()

    def get_character_time(self,i,c):
        if c == 's':
            return timedelta(seconds = int(i))
        elif c == 'm':
            return timedelta(minutes = int(i))
        elif c == 'h':
            return timedelta(hours = int(i))
        elif c == 'd':
            return timedelta(days = int(i))

    def parseRemindMe(self,message_data):
        text = message_data.get_text().split()

        if(len(text)>1):
            text_time = text[1]
            time_delta = self.get_time_delta_from_text(text_time)
        else:
            message_data.set_text("Please Specify Time: !rm ?w?d?h?m?s")
            FbClient.post_message_event(self.eb,message_data)
            return

        text_message = "REMINDER"
        if(len(text) > 2):
            text_message += ": " +  ' '.join(text[2:])

        message_data.set_text(text_message)
        send_message_event = event(EVENTID_CLIENT_SEND,message_data)
        TimeEventQueuer.post_time_event(self.eb,send_message_event,time_delta)
        
        if(time_delta>timedelta(seconds = 15)):
            time_at = datetime.datetime.now() + time_delta
            reciept_text = "Reminder set at {} in {}".format(
                    (':').join(str(time_at).split(':')[:-1]),
                    str(time_delta).split('.')[0])
            reciept_data = MessageData(reciept_text,message_data.get_id(),
                    message_data.get_type())
            FbClient.post_message_event(self.eb,reciept_data)

    def parseHelp(self,message_data):
        help_string = ""
        for line in open(help_path):
            help_string += line
        print(help_string)
        message_data.set_text(help_string)
        FbClient.post_message_event(self.eb,message_data)

    def parseRepeat(self,message_data):
        from repeating_event_object import RepeatingEventObject
        print("Parsing Repeat")
        message_data.set_text("Reapting This lol")
        send_message_event = event(EVENTID_CLIENT_SEND,message_data)
        start_time = datetime.datetime.now() + timedelta(seconds=5)
        repeat_delta = timedelta(seconds=5)
        repeat_event = RepeatingEventObject(self.eb, send_message_event,
                start_time, repeat_delta)
        repeat_event.queue()
            
    def parseWeather(self,message_data):
        self.eb.post(event(EVENTID_WEATHER_CHECK,message_data))

    def parseSubscription(self,message_data):
        print("Parsing Subscription")
        text = message_data.get_text()
        t = text.split()[1]
        if(t == "weather"):
            topic = EVENTID_WEATHER_SUBSCRIPTION
        occ = self.get_time_from_text(text)
        interval = timedelta(days = 1)
        sub = Subscription(topic,occ,interval,message_data)
        sub.post(self.eb)


    def parseIp(self,message_data):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        print("Sending Ip: " + ip)
        message_data.set_text(ip)
        message_data.show()
        FbClient.post_message_event(self.eb,message_data);


    def parse_snapshot(self,message_data):
        print("Posting snapshot event")
        self.eb.post(event(EVENTID_CLIENT_SNAPSHOT,message_data))

