import os
import ujson as json

#from bulbs import config
from bulbs.utils import build_path, get_file_path
from bulbs.element import Vertex, VertexProxy, Edge, EdgeProxy
from bulbs.index import IndexProxy
from bulbs.gremlin import Gremlin
from bulbs.yaml import YamlScripts as Scripts
from bulbs.typesystem import JSONTypeSystem

# specific to this resource
from bulbs.resource import Resource, Registry, Response, Result 
from bulbs.rest import Request, response_handlers
from typesystem import RexsterTypeSystem
from index import RexsterIndex

# The default URIs
REXSTER_URI = "http://localhost:8182/graphs/tinkergraph"
SAIL_URI = "http://localhost:8182/graphs/sailgraph"


#
# NOTE: Don't forget to reserve node 0 so users can switch if need be
#

def build_url_list(items):
    items = [str(item) for item in items]
    url_list = "[%s]" % ",".join(items)
    return url_list

def get_type_system(config):
    
    type_system_map = dict(json=(JSONTypeSystem,"application/json"),
                           rexster=(RexsterTypeSystem,"application/vnd.rexster-typed+json"))

    type_system, content_type = type_system_map[config.type_system]
    return type_system(), content_type


class RexsterResult(Result):

    def __init__(self,result):
        #self.config = config
        #self.registery = Registry()
        # rename data properties
        self.raw = result
        self.data = result

    #def get_data(self):
        #print "RESULT", 
    #    return self.result
    
    def get_id(self):
        _id = self.data['_id']
        return int(_id)
               
    def get_type(self):
        return self.data['_type']
        
    def get_uri(self):
        # TODO: we need the root_uri
        return "http://localhost:8182/graphs/...."
                 
    def get_outV(self):
        _outV = self.data.get('_outV')
        return int(_outV)
        
    def get_inV(self):
        _inV = self.data.get('_inV')
        return int(_inV)

    def get_label(self):
        return self.data.get('_label')

    def get(self,attribute):
        return self.data[attribute]



class RexsterResponse(Response):
    
    result_class = RexsterResult

    def __init__(self, response, config):
        self.handle_response(response)
        self.headers = self.get_headers(response)
        self.content = self.get_content(response)
        self.raw = self.get_raw(response,config)
        self.results, self.total_size = self.get_results()
        #self.set_extra_vars(response)

    def handle_response(self,http_resp):
        headers, content = http_resp
        response_handler = response_handlers.get(headers.status)
        response_handler(http_resp)

    def get_raw(self,response,config):
        # don't set raw in production else you'll bloat the object
        if config.debug:
            return response

    def get_headers(self,response):
        headers, content = response
        return headers

    def get_content(self,response):
        """
        http_resp is a tuple containing (headers, content)
        headers is an httplib2 Response object, content is a string
        see http://httplib2.googlecode.com/hg/doc/html/libhttplib2.html
        """
        headers, content = response
        # Neo4jServer returns empty content on update
        if content:
            content = json.loads(content)
            #print "CONTENT", content
            return content

    def get_results(self):
        #try:
        if type(self.content.get('results')) == list:
            results = (self.result_class(result) for result in self.content['results'])
            total_size = len(self.content['results'])
        elif self.content.get('results'):
            results = self.result_class(self.content['results'])
            total_size = 1
        else:
            results = None
            total_size = 0
        return results, total_size
        #except:
        #print "CONTENT", type(self.content), self.content
            # this is because delete returns no content
         #   return None, 0

    

class RexsterRequest(Request):
    
    response_class = RexsterResponse



class RexsterResource(Resource):
    
    vertex_path = "vertices"
    edge_path = "edges"
    index_path = "indices"
    gremlin_path = "tp/gremlin"
    transaction_path = "tp/batch/tx"
    multi_get_path = "tp/batch"

    def __init__(self,config):
        """
        Initializes a resource object.

        :param root_uri: the base URL of Rexster.

        """
        self.config = config
        self.config.debug = True
        self.registry = Registry()
        self.scripts = Scripts() 
        dir_name = os.path.dirname(__file__)
        self.scripts.override(get_file_path(dir_name,"gremlin.groovy"))
        self.registry.add_scripts("gremlin",self.scripts)
        self.type_system, content_type = get_type_system(config)
        self.request = RexsterRequest(config,content_type=content_type)
        #self.index_class = RexsterIndex


    #def convert_to_db(self,data):
    #    rexster_data = dict()
    #    for key, value in data.items():
    #        rexster_data[key] = self.type_system.to_db(value)
    #    return rexster_data

    #
    # Gremlin
    #
    def gremlin(self,script): 
        params = dict(script=script)
        resp = self.request.post(self.gremlin_path,params)
        return resp

    #
    # Vertices
    #
    def create_vertex(self,data):
        #data = self.convert_to_db(data)
        return self.request.post(self.vertex_path,data)

    def get_vertex(self,_id):
        path = build_path(self.vertex_path,_id)
        return self.request.get(path,params=None)

    def update_vertex(self,_id,data):
        #data = self.convert_to_db(data)
        path = build_path(self.vertex_path,_id)
        resp = self.request.put(path,data)
        #print resp.raw
        return resp

    def delete_vertex(self,_id):
        path = build_path(self.vertex_path,_id)
        return self.request.delete(path,params=None)

    #
    # Edges
    #
    def create_edge(self,outV,label,inV,data={}): 
        #data = self.convert_to_db(data)
        edge_data = dict(_outV=outV,_label=label,_inV=inV)
        data.update(edge_data)
        return self.request.post(self.edge_path,data)

    def get_edge(self,_id):
        path = build_path(self.edge_path,_id)
        return self.request.get(path,params=None)

    def update_edge(self,_id,data):
        #data = self.convert_to_db(data)
        path = build_path(self.edge_path,_id)
        resp = self.request.put(path,data)
        return resp

    def delete_edge(self,_id):
        path = build_path(self.edge_path,_id)
        return self.request.delete(path,params=None)

    #
    # Vertex Index
    #

    def create_automatic_vertex_index(self,index_name,element_class,keys=None):
        keys = json.dumps(keys) if keys else "null"
        params = dict(index_name=index_name,element_class=element_class,keys=keys)
        script = self.scripts.get('create_automatic_vertex_index',params)
        #print script
        return self.gremlin(script)
        
    def create_indexed_vertex_automatic(self,data,index_name):
        data = json.dumps(data)
        params = dict(data=data,index_name=index_name)
        script = self.scripts.get('create_automatic_indexed_vertex',params)
        print script
        return self.gremlin(script)

    def create_vertex_index(self,name,*args,**kwds):
        path = build_path(self.index_path,name)
        index_type = kwds.get('index_type','automatic')
        index_keys = kwds.get('index_keys',None)                              
        params = {'class':'vertex','type':index_type}
        if index_keys: 
            params.update({'keys':index_keys})
        return self.request.post(path,params)

    def create_edge_index(self,name,*args,**kwds):
        path = build_path(self.index_path,name)
        index_type = kwds.get('index_type','automatic')
        index_keys = kwds.get('index_keys',None)                              
        params = {'class':'edge','type':index_type}
        if index_keys: 
            params.update({'keys':index_keys})
        return self.request.post(path,params)
        
    def get_index(self,name):
        path = build_path(self.index_path,name)
        return self.request.get(path,params=None)

    def get_vertex_index(self,name):
        return self.get_index(name)

    def get_edge_index(self,name):
        return self.get_index(name)

    def get_all_indices(self):
        return self.request.get(self.index_path,params=None)
        
    def delete_index(self,name): 
        path = build_path(self.index_path,name)
        resp = self.request.delete(path,params=None)
        return resp

    def delete_vertex_index(self,name):
        self.delete_index(name)

    def delete_edge_index(self,name):
        self.delete_index(name)

    # Indexed vertices
    def put_vertex(self,name,key,value,_id):
        # Rexster's API only supports string lookups so convert value to a string 
        path = build_path(self.index_path,name)
        params = {'key':key,'value':str(value),'class':'vertex','id':_id}
        return self.request.post(path,params)

    def put_edge(self,name,key,value,_id):
        # Rexster's API only supports string lookups so convert value to a string 
        path = build_path(self.index_path,name)
        params = {'key':key,'value':str(value),'class':'edge','id':_id}
        return self.request.post(path,params)

    def lookup_vertex(self,index_name,key,value):
        path = build_path(self.index_path,index_name)
        params = dict(key=key,value=value)
        #print "PP", path, params
        return self.request.get(path,params)

    def remove_vertex(self,name,_id,key=None,value=None):
        # Can Rexster have None for key and value?
        path = build_path(self.index_path,name)
        params = {'key':key,'value':value,'class':'vertex','id':_id}
        return self.request.delete(path,params)

    def remove_edge(self,name,_id,key=None,value=None):
        # Can Rexster have None for key and value?
        path = build_path(self.index_path,name)
        params = {'key':key,'value':value,'class':'edge','id':_id}
        return self.request.delete(path,params)
    
    # Rexster-specific index mehthods
    def index_count(self,name,key,value):
        path = build_path(self.index_path,name,"count")
        params = dict(key=key,value=value)
        return self.request.get(path,params)

    def index_keys(self,name):
        path = build_path(self.index_path,name,"keys")
        #print path
        return self.request.get(path,params=None)


    # Model
    def create_indexed_vertex(self,index_name,data={},keys=None):
        script = self.scripts.create_indexed_vertex(index_name,data,keys)
        return self.gremlin(script)


    #
    # Model Proxy - Vertex
    #

    def create_indexed_vertex(self,data,index_name,keys=None):
        params = dict(data=data,index_name=index_name,keys=keys)
        script = self.scripts.get("create_indexed_vertex")
        return self.gremlin(script,params)
    
    def update_indexed_vertex(self,_id,data,index_name,keys=None):
        params = dict(_id=_id,data=data,index_name=index_name,keys=keys)
        script = self.scripts.get("update_indexed_vertex")
        return self.gremlin(script,params)




    #
    # Rexster Specific Stuff
    #
    def rebuild_vertex_index(self,index_name):
        params = dict(index_name=index_name)
        script = self.scripts.get('rebuild_vertex_index',params)
        return self.gremlin(script)

    def rebuild_edge_index(self,index_name):
        params = dict(index_name=index_name)
        script = self.scripts.get('rebuild_edge_index',params)
        return self.gremlin(script)


    # TODO: manual/custom index API

    def multi_get_vertices(self,id_list):
        path = build_path(self.multi_get_path,"vertices")
        idList = build_url_list(id_list)
        params = dict(idList=idList)
        return self.request.get(path,params)

    def multi_get_edges(self,id_list):
        path = build_path(self.multi_get_path,"edges")
        idList = build_url_list(id_list)
        params = dict(idList=idList)
        return self.request.get(path,params)

    def execute_transaction(self,transaction):
        params = dict(tx=transaction.actions)
        return self.request.post(self.transction_path,params)



