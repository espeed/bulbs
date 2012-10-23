
# NOTE: This isn't fully baked. Will probably redo this and 
# create a BatchClient like in neo4jserver/batch.py

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
          
