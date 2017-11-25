from fbchat import log, Client
from fbchat.models import *
import time
import requests
import threading
import random

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
        if message_object.text.startswith('@echo'):
            self.send(Message(text=message_object.text[6::]),
                thread_id=thread_id, thread_type=thread_type)

        # send dad joke if message start with @dad
        if message_object.text.startswith('@dad'):
            joke = requests.get('https://icanhazdadjoke.com/',
                    headers={'Accept': 'text/plain'})
            joke.encoding = 'utf-8'
            self.send(Message(text=joke.text),
                thread_id=thread_id, thread_type=thread_type)

        # send pic of best boi
        if message_object.text.startswith('@eirik'):
            r = random.randint(1, 3)
            self.sendRemoteImage(f'https://spaghettiprojecti.no/eirik/{r}.jpg',
                message=Message(text='best boi ❤️'), thread_id=thread_id,
                thread_type=thread_type)

        if message_object.text.startswith('@logout'):
            self.stopListening()

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
            print("halla fra timer")
        print ("Exiting " + self.name)

def main():
    with open('passwd.txt', 'r') as f:
        passwd = [a.strip() for a in f.readlines()]
    client = EchoBot(passwd[0], passwd[1])

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
