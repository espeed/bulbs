
class Neo4jBatch(object):
    
    def __init__(self,resource):
        self.resource = resource
        self.messages = []

    def add(self,message):
        self.messages.append(message)

    def get(self):
        return self.messages

    def execute(self):
        return self.resource.batch(self.messages)
