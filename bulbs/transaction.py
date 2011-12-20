
class Transaction(object):
    
    def __init__(self,resource):
        self.resource = resource
        self.methods = []

    def add_method(self,method,*args,**kwds):
        bundle = (method,args,kwds)
        self.methods.add(bundle)
