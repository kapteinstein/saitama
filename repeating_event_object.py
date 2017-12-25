from datetime import timedelta
from event_constants import *

"""
Repeating Event repeats itself on set intervals
eb -  to post the events on
event2execute - event that is to be executed, could be send message or other.
occurence_time - start time of first event
repeat_time - delta between repeats: defaults to two seconds
n - number of repeats: defaults to 5

to execute object do object.queue()
"""
class RepeatingEventObject():
    def __init__(self,eb,event2execute,occurence_time,repeat_time=timedelta(seconds=2),n=5):
        self.eb = eb
        self.event2execute = event2execute #Event to be posted
        self.occurence_time = occurence_time
        self.repeat_time = repeat_time
        self.n = n #number of repeats

    def get_event(self): return self.event2execute

    def queue(self):
        if(self.n==0):
            print("RepeatingEvent Finished")
            return

        from datetime import datetime
        from time_event_queuer import TimeEventQueuer
        from geeteventbus.event import event

        self.n-=1
        # print("Posting REPEATING event")
        while(datetime.now() > self.occurence_time):
            self.occurence_time += self.repeat_time
        delta_time = self.occurence_time - datetime.now()
        time_event = event( EVENTID_REPEATING, self)
        TimeEventQueuer.post_time_event(self.eb, time_event, delta_time)

