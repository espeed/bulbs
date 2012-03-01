
class Neo4jBatch(object):
    
    def __init__(self,client):
        self.client = client
        self.messages = []
        self.message_id = 0

    def __lshift__(self,message):
        self.add(message)

    def next_id(self):
        self.message_id = self.message_id + 1
        return self.message_id

    def placeholder(self,message_id):
        return "{%d}" % message_id

    def add(self,message):
        message_id = self.next_id()
        method, path, params = message
        message = dict(method=method, to=path, body=params, id=message_id)
        self.messages.append(message)
        return self.placeholder(message_id)

    def get(self):
        return self.messages

    def send(self):
        return self.client.batch(self.messages)
