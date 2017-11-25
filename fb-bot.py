from fbchat import log, Client
from fbchat.models import *
import time
import requests

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

def main():
    client = EchoBot('kongerik1@gmail.com', 'Qq888888')
    client.listen()
    client.logout()

if __name__ == "__main__":
    main()
