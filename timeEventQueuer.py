from geeteventbus.subscriber import subscriber
from geeteventbus.eventbus import eventbus
from geeteventbus.event import event

import time
import requests
import threading
import random
from datetime import datetime, timedelta
import heapq

EVENTID_TIME = "Topic: Time Event"
EVENTID_REPEATING = "Topic: Repeating Event"
EVENTID_QUEUE_START = "Topic: Start Event Queue"
EVENTID_QUEUE_STOP = "Topic: Stop Event Queue"

"""
Event Queuer for Time Events

Executes the heap on top of heap sorted on time.
Post timeEvents to eventBus with desired topics and possible other data

Edit execute_event to fit execution process of event

The Queuer must be added as a subscriber to the event bus on the desired topics
"""
class Time_event_queuer(threading.Thread,subscriber):
    def __init__(self,eb,cv):
        super().__init__()
        self.eb = eb #Event Bus
        self.cv = cv  #Conditional Variable, used for notifying on events
        self.heap = []
        self.execute_flag = False
        self.new_event_flag = False #Set when a new event is added to the queue

    #Executes the event on top of heap. Must be popped
    def execute_event(self):
        e = heapq.heappop(self.heap)
        if(isinstance(e[1],event)):
            new_event = e[1]
            if(new_event.get_topic() == EVENTID_REPEATING):
                repeating_event = new_event.get_data()
                self.eb.post(repeating_event.get_event())
                print("POSTING NEW TIME EVEEENT")
                Time_event_queuer.post_repeating_event(self.eb,repeating_event)
            else:
                self.eb.post(e[1])

    #Listens on the bus 
    def process(self,new_event):
        print(new_event.get_topic())
        if not isinstance(new_event,event):
            print("Invalid event type passed")
            return
        if new_event.get_topic() == EVENTID_TIME:
            self.add_event(new_event)
        elif new_event.get_topic() == EVENTID_QUEUE_START:
            self.start_queue_loop()
        elif new_event.get_topic() == EVENTID_QUEUE_STOP:
            self.stop_queue_loop()

    def run(self):
        self.eb.register_consumer(self,EVENTID_TIME)
        self.eb.register_consumer(self,EVENTID_QUEUE_START)
        self.eb.register_consumer(self,EVENTID_QUEUE_STOP)
        self.start_queue_loop()

    #Starts the queue loop on EVENTID_QUEUE_START event
    def start_queue_loop(self):
        self.execute_flag = True
        self.run_state()
        
    #Stops the queue loop on EVENTID_QUEUE_STOP event
    def stop_queue_loop(self):
        print("Stopping queuer in {}".format(threading.current_thread().__class__.__name__))
        self.execute_flag = False
        with self.cv:
            self.cv.notify() 

    #Runs the queue is not empty and the execution flag is True
    def run_state(self):
        print("TimeQueuer Running")
        while(self.execute_flag):
            if(self.heap_empty()):
                self.idle_state()
                return
            with self.cv:
                self.new_event_flag = False
                t = self.get_sleep_time()
                ne = self.get_event()
                print("Next event: {} in {}".format(ne[1],t))
                self.cv.wait(t)
                if(self.new_event_flag):
                    continue
                if(self.execute_flag):
                    self.execute_event()
        print("Queuer Stopped from Running State")
        
    #Idle when the queue is empty and the exectuion flag is True
    def idle_state(self):
        while(self.execute_flag):
            if(not self.heap_empty()):
                self.run_state()
                return
            print("TimeQueuer Idle - Execute _flag: {}".format(self.execute_flag))
            with self.cv:
                self.cv.wait()
        print("Queuer Stopped from Idle State")
                
    #Calculage sleep time until top of heap event
    def get_sleep_time(self):
        if(len(self.heap)==0):
            print("ERROR: No event in queue to evaluate")
            return None
        te = self.heap[0][0]
        tn = datetime.now()
        
        td = te - tn
        td = td.total_seconds()
        return td
        
    #Add new event to heap, set new_event_flag and notify Conditional Variable
    def add_event(self,new_event):
            heapq.heappush(self.heap,new_event.get_data())
            self.new_event_flag = True
            with self.cv:
                self.cv.notify()

    #Pops the event on top of heap
    def pop_event(self):
        return heapq.heappop(self.heap)

    #Gets the event on top of heap
    def get_event(self):
        return self.heap[0]

    #Returns True if Heap is Empty
    def heap_empty(self):
        return len(self.heap)==0
    
    @staticmethod
    def post_time_event(eb,data,delta_time):
        event_time = datetime.now() + delta_time #ms removed
        print("EVENT scheduled at {}".format(event_time))
        data = (event_time,data)
        eb.post(event(EVENTID_TIME,data))

    @staticmethod
    def post_repeating_event(eb,repeating_event_object):
        print("Posting REPEATING event")
        event_time = repeating_event_object.occurence_start
        now = datetime.now()
        while(now > event_time):
            event_time += repeating_event_object.repeat_delta
        delta_time = event_time - datetime.now()
        Time_event_queuer.post_time_event(eb,event(EVENTID_REPEATING,repeating_event_object),
                delta_time)

class Repeating_event_object():
    def __init__(self,event,occurence_start,repeat_delta):
        self.event = event #Event to be posted
        self.occurence_start = occurence_start
        self.repeat_delta = repeat_delta

    def get_event(self): return self.event



class Thread_handler():
    def __init__(self,eb):
        self.threads = []
        self.eb = eb

    def add_thread(self,threadObject):
        self.threads.append(threadObject)
        
    def start_threads(self):
        for t in self.threads:
            print("Registering consumer")
            self.eb.register_consumer(t,EVENTID_TIME)
            self.eb.register_consumer(t,EVENTID_QUEUE_START)
            self.eb.register_consumer(t,EVENTID_QUEUE_STOP)
            t.start()
        self.eb.post(event(EVENTID_QUEUE_START,""))

    def join_threads(self):
        self.eb.post(event(EVENTID_QUEUE_STOP,""))
        for t in self.threads:
            print("Joining thread: {}".format(t.getName()))
            t.join()


def main():
    # Create Thread Handler
    eb = eventbus()
    th = Thread_handler(eb)
    cv = threading.Condition()

    # Create new threads
    teq = Time_event_queuer(eb,cv)
    teq.start()
    th.add_thread(teq)
    
    # Start new Threads
    #th.start_threads()

    # Post Information
    teq.post_time_event(eb,"post1",timedelta(seconds=3))
    time.sleep(2)
    teq.post_time_event(eb,"post2",timedelta(seconds=10))
    time.sleep(2)
    teq.post_time_event(eb,"post3",timedelta(seconds=6))
    time.sleep(1)
    teq.post_time_event(eb,"post4",timedelta(seconds=1))
    time.sleep(1)
    teq.post_time_event(eb,"post5",timedelta(seconds=2))
    time.sleep(1)
    
    # Stopping threads
    #th.join_threads()
    eb.post(event(EVENTID_QUEUE_STOP,""))
    teq.join()
    
    

    print ("Exiting Main Thread")
    eb.shutdown()


if __name__ == "__main__":
    main()
