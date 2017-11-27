from fbchat import log, Client
from fbchat.models import *
import time
import requests
import threading
import random
import datetime

_BASE_URL = 'http://spaghettiprojecti.no/saitama/'
_THREAD_ID = '1434497743266652'

# Subclass fbchat.Client and override required methods
class EchoBot(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(author_id, thread_id)
        self.markAsRead(author_id)

        log.info("{} from {} in {}".format(message_object, thread_id, thread_type.name))

        # If Saitama-san is the author -> sayonara
        if author_id == self.uid:
            return

        # echo if message start with @echo
        if message_object.text.startswith('!echo'):
            self.send(Message(text=message_object.text[6::]),
                thread_id=thread_id, thread_type=thread_type)

        # send dad joke if message start with @dad
        if '!dad' in message_object.text:
            joke = requests.get('https://icanhazdadjoke.com/',
                    headers={'Accept': 'text/plain'})
            joke.encoding = 'utf-8'
            self.send(Message(text=joke.text),
                thread_id=thread_id, thread_type=thread_type)

        # send pic of best boi
        if '!eirik' in message_object.text:
            r = random.randint(1, 3)
            url = _BASE_URL + 'eirik/' + str(r) + '.jpeg'
            self.sendRemoteImage(url, message=Message(text='best boi ❤️'),
                    thread_id=thread_id, thread_type=thread_type)

        if '!logout' in message_object.text:
            self.logout_request = True
            self.stopListening()

    def timer(self):
        sent_today = False
        while not self.logout_request:
            time.sleep(1)
            now = datetime.datetime.now()
            if (now.month == 12 and now.day <= 24 and now.hour == 8 and not
                    sent_today):
                url = _BASE_URL + 'julekalender/' + str(now.day) + '.jpeg'
                msg = 'saitamas julekalender, luke ' + str(now.day)
                self.sendRemoteImage(url, message=Message(text=msg),
                        thread_id=_THREAD_ID, thread_type=thread_type.GROUP)
                sent_today = True
            if now.hour == 0 and sent_today:
                sent_today = False


class Bot_thread(threading.Thread):
    def __init__(self, threadID, name, client):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.client = client
    def run(self):
        print ("Starting " + self.name)
        if self.name == "listener":
            self.client.listen()
        if self.name == "timer":
            self.client.timer()
        print ("Exiting " + self.name)


def main():
    with open('passwd.txt', 'r') as f:
        passwd = [a.strip() for a in f.readlines()]
    client = EchoBot(passwd[0], passwd[1])
    client.logout_request = False

    # Create new threads
    thread1 = Bot_thread(1, "listener", client)
    thread2 = Bot_thread(2, "timer", client)

    # Start new Threads
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    if client.isLoggedIn():
        client.logout()

    print ("Exiting Main Thread")


if __name__ == "__main__":
    main()
