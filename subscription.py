from geeteventbus.event import event

class Subscription():
    def __init__(self,topic,occurrence,interval,data):
        self.topic = topic
        self.occurrence = occurrence #datetime object
        self.interval = interval #timedelta object
        self.data = data #subscription data, e.g. message data

    def get_occurrence(self):
        return self.occurrence
    
    def get_interval(self):
        return self.interval

    def get_data(self):
        return self.data

    def post(self,eb):
        eb.post(event(self.topic,self))


