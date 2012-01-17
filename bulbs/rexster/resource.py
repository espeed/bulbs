# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Bulbs supports pluggable resources. This is the Rexster resource.

"""

import os
import ujson as json

#from bulbs import config
from bulbs.utils import build_path, get_file_path
from bulbs.element import Vertex, VertexProxy, Edge, EdgeProxy
#from bulbs.index import IndexProxy
from bulbs.gremlin import Gremlin
from bulbs.groovy import GroovyScripts as Scripts
from bulbs.typesystem import JSONTypeSystem

# specific to this resource
from bulbs.resource import Resource, Registry, Response, Result 
from bulbs.rest import RESPONSE_HANDLERS, Request
from index import ManualIndex

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
    
    type_system_map = dict(json=(JSONTypeSystem,"application/json"))

    type_system, content_type = type_system_map[config.type_system]
    return type_system(), content_type


class RexsterResult(Result):

    def __init__(self,result):
        self.raw = result
        self.data = result

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

    def __init__(self, response):
        self.handle_response(response)
        self.headers = self.get_headers(response)
        self.content = self.get_content(response)
        self.results, self.total_size = self.get_results()
        self.raw = response

    def handle_response(self,http_resp):
        headers, content = http_resp
        response_handler = RESPONSE_HANDLERS.get(headers.status)
        response_handler(http_resp)

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
        if content:
            content = json.loads(content)
            return content

    def get_results(self):
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
        self.registry = Registry(config)
        self.scripts = Scripts() 
        self.scripts.update(self._get_scripts_file("gremlin.groovy"))
        self.registry.add_scripts("gremlin",self.scripts)
        self.type_system, content_type = get_type_system(config)
        self.request = RexsterRequest(config,content_type=content_type)
        #self.index_class = ManualIndex


    #def convert_to_db(self,data):
    #    rexster_data = dict()
    #    for key, value in data.items():
    #        rexster_data[key] = self.type_system.to_db(value)
    #    return rexster_data

    #
    # Gremlin
    #
    def gremlin(self,script,params=None): 
        params = dict(script=script,params=params)
        return self.request.post(self.gremlin_path,params)

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
        return self.request.put(path,data)
        
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
        return self.request.put(path,data)

    def delete_edge(self,_id):
        path = build_path(self.edge_path,_id)
        return self.request.delete(path,params=None)

    # Vertex Container

    def outE(self,_id,label=None):
        """Return the outgoing edges of the vertex."""
        script = self.scripts.get('outE')
        params = dict(_id=_id,label=label)
        return self.gremlin(script,params)

    def inE(self,_id,label=None):
        """Return the incoming edges of the vertex."""
        script = self.scripts.get('inE')
        params = dict(_id=_id,label=label)
        return self.gremlin(script,params)

    def bothE(self,_id,label=None):
        """Return all incoming and outgoing edges of the vertex."""
        script = self.scripts.get('bothE')
        params = dict(_id=_id,label=label)
        return self.gremlin(script,params)

    def outV(self,_id,label=None):
        """Return the out-adjacent vertices to the vertex."""
        script = self.scripts.get('outV')
        params = dict(_id=_id,label=label)
        return self.gremlin(script,params)
        
    def inV(self,_id,label=None):
        """Return the in-adjacent vertices of the vertex."""
        script = self.scripts.get('inV')
        params = dict(_id=_id,label=label)
        return self.gremlin(script,params)
        
    def bothV(self,_id,label=None):
        """Return all incoming- and outgoing-adjacent vertices of vertex."""
        script = self.scripts.get('bothV')
        params = dict(_id=_id,label=label)
        return self.gremlin(script,params)


    #
    # Index Proxy - Vertex
    #

    def create_vertex_index(self,index_name,*args,**kwds):
        path = build_path(self.index_path,index_name)
        index_type = kwds.get('index_type','manual')
        index_keys = kwds.get('index_keys',None)                              
        params = {'class':'vertex','type':index_type}
        if index_keys: 
            params.update({'keys':index_keys})
        return self.request.post(path,params)

    def create_edge_index(self,name,*args,**kwds):
        path = build_path(self.index_path,name)
        index_type = kwds.get('index_type','manual')
        index_keys = kwds.get('index_keys',None)                              
        params = {'class':'edge','type':index_type}
        if index_keys: 
            params.update({'keys':index_keys})
        return self.request.post(path,params)
        
    #def create_automatic_vertex_index(self,index_name,element_class,keys=None):
    #    keys = json.dumps(keys) if keys else "null"
    #    params = dict(index_name=index_name,element_class=element_class,keys=keys)
    #    script = self.scripts.get('create_automatic_vertex_index',params)
    #    return self.gremlin(script)
        
    #def create_indexed_vertex_automatic(self,data,index_name):
    #    data = json.dumps(data)
    #    params = dict(data=data,index_name=index_name)
    #    script = self.scripts.get('create_automatic_indexed_vertex',params)
    #    return self.gremlin(script)

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
        try:
            path = build_path(self.index_path,name)
            return self.request.delete(path,params=None)
        except LookupError:
            return None
            

    def delete_vertex_index(self,name):
        self.delete_index(name)

    def delete_edge_index(self,name):
        self.delete_index(name)



    # Indexed vertices
    def put_vertex(self,index_name,key,value,_id):
        # Rexster's API only supports string lookups so convert value to a string 
        path = build_path(self.index_path,index_name)
        params = {'key':key,'value':str(value),'class':'vertex','id':_id}
        return self.request.put(path,params)

    def put_edge(self,index_name,key,value,_id):
        # Rexster's API only supports string lookups so convert value to a string 
        path = build_path(self.index_path,index_name)
        params = {'key':key,'value':str(value),'class':'edge','id':_id}
        return self.request.put(path,params)

    def lookup_vertex(self,index_index_name,key,value):
        path = build_path(self.index_path,index_index_name)
        params = dict(key=key,value=value)
        return self.request.get(path,params)

    def remove_vertex(self,index_name,_id,key=None,value=None):
        # Can Rexster have None for key and value?
        path = build_path(self.index_path,index_name)
        params = {'key':key,'value':value,'class':'vertex','id':_id}
        return self.request.delete(path,params)

    def remove_edge(self,index_name,_id,key=None,value=None):
        # Can Rexster have None for key and value?
        path = build_path(self.index_path,index_name)
        params = {'key':key,'value':value,'class':'edge','id':_id}
        return self.request.delete(path,params)
    
    # Rexster-specific index mehthods
    def index_count(self,index_name,key,value):
        path = build_path(self.index_path,index_name,"count")
        params = dict(key=key,value=value)
        return self.request.get(path,params)

    def index_keys(self,index_name):
        path = build_path(self.index_path,index_name,"keys")
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
    # Model Proxy - Edge
    #

    def create_indexed_edge(self,data,index_name,keys=None):
        params = dict(data=data,index_name=index_name,keys=keys)
        script = self.scripts.get("create_indexed_edge")
        return self.gremlin(script,params)
    
    def update_indexed_edge(self,_id,data,index_name,keys=None):
        params = dict(_id=_id,data=data,index_name=index_name,keys=keys)
        script = self.scripts.get("update_indexed_edge")
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

    def _get_scripts_file(self,file_name):
        dir_name = os.path.dirname(__file__)
        file_path = get_file_path(dir_name,file_name)
        return file_path

