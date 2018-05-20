
class MessageData():
    def __init__(self,text,thread_id,thread_type):
        self.text = text
        self.thread_id = thread_id
        self.thread_type = thread_type

    def get_text(self): return self.text
    def set_text(self,text): self.text = text
    def get_id(self,): return self.thread_id
    def get_type(self,): return self.thread_type

    def show(self):
        print("Show data: {} {} {}".format(self.text,self.thread_id,self.thread_type))

