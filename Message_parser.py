from FbClient import *
from geeteventbus.event import event
from datetime import datetime, timedelta

TIME_KEYES = ['d','h','m','s']
class Message_parser():
    def __init__(self,event_bus):
        self.eb = event_bus

    def parse(self,message_data):
        text = message_data.get_text()
        print(text)
        # echo if message start with @echo
        if text.startswith('!echo'):
            print("Echoing")
            message_data.set_text(text[6::])
            Fb_client.post_message_event(self.eb,message_data)
            return

        # send dad joke if message start with @dad
        if '!dad' in text:
            print("Dading")
            joke = requests.get('https://icanhazdadjoke.com/',
                    headers={'Accept': 'text/plain'})
            joke.encoding = 'utf-8'
            message_data.set_text(joke.text)
            Fb_client.post_message_event(self.eb,message_data)
            return

        if '!logout' in text:
            print("Posting Stop event")
            self.eb.post(event(EVENTID_CLIENT_STOP,""))

        elif text.startswith('!rm'):
            self.parseRemindMe(message_data)

        elif text.startswith('!help'):
            self.parseHelp(message_data)

        elif text.startswith('!repeat'):
            self.parseRepeat(message_data)

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
            Fb_client.post_message_event(self.eb,message_data)
            return

        text_message = "REMINDER"
        if(len(text) > 2):
            text_message += ": " +  ' '.join(text[2:])

        message_data.set_text(text_message)
        send_message_event = event(EVENTID_CLIENT_SEND,message_data)
        Time_event_queuer.post_time_event(self.eb,send_message_event,time_delta)
        
        if(time_delta>timedelta(seconds = 15)):
            time_at = datetime.now() + time_delta
            reciept_text = "Reminder set at {} in {}".format(
                    (':').join(str(time_at).split(':')[:-1]),
                    str(time_delta).split('.')[0])
            reciept_data = Message_data(reciept_text,message_data.get_id(),
                    message_data.get_type())
            Fb_client.post_message_event(self.eb,reciept_data)

    def parseHelp(self,message_data):
            message_data.set_text("Help is on the way")
            Fb_client.post_message_event(self.eb,message_data)

    def parseRepeat(self,message_data):
        print("Parsing Repeat")
        message_data.set_text("Reapting This lol")
        send_message_event = event(EVENTID_CLIENT_SEND,message_data)
        start_time = datetime.now() + timedelta(seconds=5)
        repeat_delta = timedelta(seconds=5)
        repeat_event = Repeating_event_object(self.eb, send_message_event,
                start_time, repeat_delta)
        repeat_event.queue()
            


