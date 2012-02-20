
class RexsterTransaction(object):

    def __init__(self):
        self.actions = []

    def create_edge(self,outV,label,inV,data={}):
        edge_data = dict(_outV=outV,_label=label,_inV=inV)
        data.update(edge_data)
        action = build_action("create","edge",data)
        self.actions.append(action)

    def build_action(self,_action,_type,data={}):
        action = {'_action':_action,'_type':_type}
        for key in data:  # Python 3
            value = data[key]
            action.update({key:value})
        return action              
          
class Neo4jTransaction(object):
    
    def __init__(self):
        self.actions = []

    
    def build_action(self,method,to,body={},request_id=None):
        # method: GET, POST, PUT, DELETE
        # to: relative path, e.g. /node, /node/0, /node/0/properties
        # body: dict(age=34)
        # request_id: a user-supplied ID for keeping track of responses
        action = {'method':method,'to':to,'body':body}
        if request_id is not None:
            action.update({'id':request_id})
        
        for key in data:  # Python 3
            value = data[key]
            action.update({key:value})
        return action              
