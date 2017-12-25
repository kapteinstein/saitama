
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
