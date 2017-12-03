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

        if text.startswith('!rm'):
            self.parseRemindMe(message_data)

        if text.startswith('!help'):
            self.parseHelp(message_data)

    def get_message_time(self,i,c):
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

        text_time = text[1]
        time_delta = timedelta(seconds=0)
        number = ""
        for c in text_time:
            if(c.isdigit()):
                number += c
            if(c in TIME_KEYES):
                time_delta += self.get_message_time(number,c)
                number = ""

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

            


