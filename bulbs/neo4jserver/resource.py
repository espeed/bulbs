# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""

Bulbs supports pluggable backends. This is the Neo4j Server resource.

"""
import ujson as json

from bulbs.utils import build_path, get_file_path
from bulbs.registry import Registry

# specific to this resource
from bulbs.resource import Resource, Response, Result
from bulbs.rest import Request, response_handlers
from bulbs.groovy import GroovyScripts as Scripts
from bulbs.typesystem import JSONTypeSystem
from index import Neo4jIndex
import os

# The default URI
NEO4J_URI = "http://localhost:7474/db/data/"


class Neo4jResult(Result):
    """
    Container class for a single result, not a list of results.

    :param result: The raw result.
    :type result: dict

    """

    def __init__(self,result):
        #: The raw result.
        self.raw = result

        #: The data in the result.
        self.data = result.get('data')
        
    def get_id(self):
        """Returns the element ID."""
        uri = self.raw.get('self')
        return self._parse_id(uri)
       
    def get_type(self):
        """Returns the element's base type, either vertex or edge."""
        type_map = dict(node="vertex",relationship="edge")
        uri = self.get_uri()
        neo4j_type = self._parse_type(uri)
        return type_map[neo4j_type]
        
    def get_uri(self):
        """Returns the element URI."""
        return self.raw.get('self')
                 
    def get_outV(self):
        """Returns the ID of the edge's outgoing vertex (start node)."""
        uri = self.raw.get('start')
        return self._parse_id(uri)
        
    def get_inV(self):
        """Returns the ID of the edge's incoming vertex (end node)."""
        uri = self.raw.get('end')
        return self._parse_id(uri)

    def get_label(self):
        """Returns the edge label (relationship type)."""
        return self.raw.get('type')

    def get(self,attribute):
        """Returns the value of a resource-specific attribute."""
        return self.raw[attribute]

    def _parse_id(self,uri):
        """Parses the ID out of a URI."""
        if uri:
            _id = int(uri.rpartition('/')[-1])
            return _id

    def _parse_type(self,uri):
        """Parses the type ouf of a URI."""
        if uri:
            root_uri = uri.rpartition('/')[0]
            neo4j_type = root_uri.rpartition('/')[-1]
            return neo4j_type


class Neo4jResponse(Response):
    
    result_class = Neo4jResult

    def __init__(self, response):
        self.handle_response(response)
        self.headers = self.get_headers(response)
        self.content = self.get_content(response)
        self.results, self.total_size = self.get_results()
        self.raw = response

    def handle_response(self,response):
        headers, content = response
        response_handler = response_handlers.get(headers.status)
        response_handler(response)

    def get_headers(self,response):
        headers, content = response
        return headers

    def get_content(self,response):
        """
        response is a tuple containing (headers, content)
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
        if type(self.content) == list:
            results = (self.result_class(result) for result in self.content)
            total_size = len(self.content)
        elif self.content and self.content != "null":
            # checking for self.content.get('data') won't work b/c the data value
            # isn't returned for edges with no properties
            # The get data thing may be a hack, or it may be what's needed. Don't know yet.
            # and self.content != "null":
            # Yep, the null thing is sort of a hack. 
            # Neo4j returns "null" if Gremlin scripts don't return anything.
            results = self.result_class(self.content)
            total_size = 1
        else:
            results = None
            total_size = 0
        return results, total_size


class Neo4jRequest(Request):
    
    response_class = Neo4jResponse


class Neo4jResource(Resource):

    vertex_path = "node"
    edge_path = "relationships"
    index_path = "index"
    gremlin_path = "ext/GremlinPlugin/graphdb/execute_script"
    cypher_path = "ext/CypherPlugin/graphdb/execute_query"
    #cypher_path = "cypher"

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
        self.type_system = self._get_type_system()
        self.request = Neo4jRequest(config,self.type_system.content_type)
        #self.index_class = Neo4jIndex
        
    #
    # Gremlin
    #

    def gremlin(self,script,params=None): 
        #print script
        params = dict(script=script,params=params)
        return self.request.post(self.gremlin_path,params)

    #
    # Cypher
    #

    def cypher(self,query,params=None):
        params = dict(query=query,params=params)
        return self.request.post(self.cypher_path,params)
        
    #
    # Vertex Proxy
    #

    def create_vertex(self,data):
        #print "CREATEEEEEEEE"
        # TODO: remove None values
        return self.request.post(self.vertex_path,data)

    def get_vertex(self,_id):
        path = build_path(self.vertex_path,_id)
        return self.request.get(path,params=None)
        
    def update_vertex(self,_id,data):
        path = build_path(self.vertex_path,_id,"properties")
        return self.request.put(path,data)

    def delete_vertex(self,_id):
        # Neo4j requires you delete all adjacent edges first. 
        # But the Neo4jServer DELETE URI doesn't do this so 
        # I created a Gremlin method for it. - James
        params = dict(_id=_id)
        script = self.scripts.get("delete_vertex")
        resp = self.gremlin(script,params)
        #print "RAAAAAAAAAAAAA", resp.raw
        return resp

    #
    # Edge Proxy
    #

    def create_edge(self,outV,label,inV,data={}): 
        # TODO: remove None values
        path = build_path(self.vertex_path,outV,self.edge_path)
        inV_uri = "%s/node/%s" % (self.config.root_uri.rstrip("/"), inV)
        params = {'to':inV_uri,'type':label, 'data':data}
        resp = self.request.post(path,params)
        #print "EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE", resp.raw
        return resp

    def get_edge(self,_id):
        path = build_path("relationship",_id)
        return self.request.get(path,params=None)
        
        #path = build_path(self.edge_path,_id)
        #script = "g.e(%s)" % _id
        #return self.gremlin(script)

    def update_edge(self,_id,data):
        path = build_path("relationship",_id,"properties")
        return self.request.put(path,data)

    def delete_edge(self,_id):
        # note relationship path is singular, not plural
        path = build_path("relationship",_id)
        return self.request.delete(path,params=None)


    #
    # Vertex Container
    #

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
        index_type = kwds.pop("index_type","exact")
        provider = kwds.pop("provider","lucene")
        #keys = kwds.pop("keys",None)
        #keys = json.dumps(keys) if keys else "null"
        #config = {'type':index_type,'provider':provider,'keys':str(keys)}
        config = {'type':index_type,'provider':provider}
        path = build_path(self.index_path,"node")
        params = dict(name=index_name,config=config)
        return self.request.post(path,params)

    def get_vertex_indices(self):
        # returns a map of indices
        path = build_path(self.index_path,"node")
        return self.request.get(path,params=None)

    def get_vertex_index(self,name):
        # this is pretty much a hack becuase the way neo4j does this is inconsistent
        resp = self.get_vertex_indices()
        resp.results = None   # for clarity
        result = resp.content.get(name)
        if result:
            result['name'] = name
            resp.results = Neo4jResult(result)
        #print "INDEX", resp.raw
        return resp

    def delete_vertex_index(self,name): 
        path = build_path(self.index_path,"node",name)
        return self.request.delete(path,params=None)

    #
    # Index Proxy - Edge
    #

    def create_edge_index(self,index_name,*args,**kwds):
        path = build_path(self.index_path,"relationship")
        params = dict(name=index_name)
        return self.request.post(path,params)

    def get_edge_indices(self):
        path = build_path(self.index_path,"relationship")
        return self.request.get(path,params=None)

    def get_edge_index(self,name):
        # this is pretty much a hack becuase the way neo4j does this is inconsistent
        resp = self.get_edge_indices()
        resp.results = None   # for clarity
        result = resp.content.get(name)
        if result:
            result['name'] = name
            resp.results = Neo4jResult(result)
        return resp

    def delete_edge_index(self,name):
        pass

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
        raise NotImplementedError 

    def update_indexed_edge(self,_id,data,index_name,keys=None):
        raise NotImplementedError 


    #
    # Utils
    #

    def warm_cache(self):
        script = self.scripts.get('warm_cache')
        return self.gremlin(script,params=None)

    #
    # Deprecated 
    #

    # Indexed vertices
    def add_vertex_to_index(self,name,key,value,_id):
        path = build_path(self.index_path,"node",name,key,value)
        node_uri = "%s/%d" % (self.config.root_uri,_id)
        return self.request.post(path,params=node_uri)

    def lookup_vertex(self,name,key,value):
        path = build_path(self.index_path,"node",name,key,value)
        return self.request.get(path,params=None)

    def query_vertex(self,name,params):
        path = build_path(self.index_path,"node",name)
        return self.request.get(path,params)

    def remove_vertex_from_index(self,name,_id,key=None,value=None):
        #if key is not None and value is not None:
        #    path = build_path("node",name,key,value,_id)
        #elif key is not None:
        #    path = build_path("node",name,key,_id)
        #else:
        #    path = build_path("node",name,_id)
        path = build_path("node",name,key,value,_id)
        return self.request.delete(path,params=None)
    
    def _get_type_system(self):
        type_system_map = dict(json=JSONTypeSystem())
        type_system = type_system_map[self.config.type_system]
        return type_system()
