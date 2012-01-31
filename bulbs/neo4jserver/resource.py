# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""

Bulbs supports pluggable backends. This is the Neo4j Server resource.

"""
import os
import ujson as json
from urlparse import urlsplit

from bulbs.utils import get_file_path, get_logger
from bulbs.registry import Registry
from bulbs.config import DEBUG

# specific to this resource
from bulbs.resource import Resource, Response, Result
from bulbs.rest import Request, RESPONSE_HANDLERS
from bulbs.typesystem import JSONTypeSystem
from bulbs.groovy import GroovyScripts
from message import Message

# The default URI
NEO4J_URI = "http://localhost:7474/db/data/"

# The logger defined in Config
log = get_logger(__name__)


class Neo4jResult(Result):
    """
    Container class for a single result, not a list of results.

    :param result: The raw result.
    :type result: dict

    :param config: The resource Config object.
    :type config: Config 

    """

    def __init__(self,result, config):
        self.config = config

        #: The raw result.
        self.raw = result

        #: The data in the result.
        self.data = self._get_data(result)

        self.type_map = dict(node="vertex",relationship="edge")

    def get_id(self):
        """Returns the element ID."""
        uri = self.raw.get('self')
        return self._parse_id(uri)
       
    def get_type(self):
        """Returns the element's base type, either vertex or edge."""
        uri = self.get_uri()
        neo4j_type = self._parse_type(uri)
        return self.type_map[neo4j_type]
        
    def get_map(self):
        """Returns the element's property map."""
        return self.data

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

    def get_index_class(self):
        """Returns the index class (either "vertex" or "edge")."""
        uri = self.raw.get('template') 
        neo4j_type = self._parse_index_type(uri)
        return self.type_map[neo4j_type]

    def get(self,attribute):
        """Returns the value of a resource-specific attribute."""
        return self.raw[attribute]

    def _get_data(self,result):
        if type(result) is dict:
            return result.get('data') 

    def _parse_id(self,uri):
        """Parses the ID out of a URI."""
        if uri:
            _id = int(uri.rpartition('/')[-1])
            return _id

    def _parse_type(self,uri):
        """Parses the type ouf of a normal URI."""
        if uri:
            root_uri = uri.rpartition('/')[0]
            #print root_uri
            neo4j_type = root_uri.rpartition('/')[-1]
            return neo4j_type
    
    def _parse_index_type(self,uri):
        """Parses the type out of an index URI."""
        if uri:
            path = urlsplit(uri).path
            segments = path.split("/")
            neo4j_type = segments[-4]
            return neo4j_type


class Neo4jResponse(Response):
    
    result_class = Neo4jResult

    def __init__(self, response, config):
        self.config = config
        self.handle_response(response)
        self.headers = self.get_headers(response)
        self.content = self.get_content(response)
        self.results, self.total_size = self.get_results()
        self.raw = self._maybe_get_raw(response, config)

    def _maybe_get_raw(self,response, config):
        # don't store raw response in production else you'll bloat the obj
        if config.log_level == DEBUG:
            return response

    def handle_response(self,response):
        """Handle HTTP server response."""
        headers, content = response
        response_handler = RESPONSE_HANDLERS.get(headers.status)
        response_handler(response)

    def get_headers(self,response):
        """Return the headers from the HTTP response."""
        headers, content = response
        return headers

    def get_content(self,response):
        """Return the content from the HTTP response."""
        
        # response is a tuple containing (headers, content)
        # headers is an httplib2 Response object, content is a string
        # see http://httplib2.googlecode.com/hg/doc/html/libhttplib2.html
        headers, content = response

        # Neo4jServer returns empty content on update
        if content:
            content = json.loads(content)
            return content

    def get_results(self):
        """Return results from response, formatted as Result objects, and its total size."""
        if type(self.content) == list:
            results = (self.result_class(result, self.config) for result in self.content)
            total_size = len(self.content)
        elif self.content and self.content != "null":
            # Checking for self.content.get('data') won't work b/c the data value
            # isn't returned for edges with no properties;
            # and self.content != "null": Yep, the null thing is sort of a hack. 
            # Neo4j returns "null" if Gremlin scripts don't return anything.
            results = self.result_class(self.content, self.config)
            total_size = 1
        else:
            results = None
            total_size = 0
        return results, total_size

    def set_index_name(self,index_name):
        """Sets the index name to the raw result."""
        # this is pretty much a hack becuase the way neo4j does this is inconsistent
        self.results.raw['name'] = index_name
        

class Neo4jRequest(Request):
    """Makes requests to Neo4j Server and returns a Neo4jResponse.""" 
    
    response_class = Neo4jResponse


class Neo4jResource(Resource):
    """Low-level client that connects to Neo4j Server and returns a response.""" 

    def __init__(self,config):
        self.config = config
        self.registry = Registry(config)
        self.scripts = GroovyScripts()
        self.scripts.update(self._get_scripts_file("gremlin.groovy"))
        self.registry.add_scripts("gremlin",self.scripts)
        self.type_system = JSONTypeSystem()
        self.request = Neo4jRequest(config,self.type_system.content_type)
        self.message = Message(config, self.scripts)
        
    # Gremlin

    def gremlin(self,script,params=None): 
        """Executes a Gremlin script and returns the Response."""
        message = self.message.gremlin(script,params)
        return self.request.send(message)

    # Cypher

    def cypher(self,query,params=None):
        """Executes a Cypher query and returns the Response."""
        message = self.message.cypher(query,params)
        resp = self.request.send(message)
        # Cypher data hack
        resp.results = (self.result_class(result[0], self.config) for result in resp.results.data)
        resp.total_size = len(resp.results.data)
        return resp

    # Vertex Proxy

    def create_vertex(self,data):
        """Creates a vertex and returns the Response."""
        if self.config.autoindex is True:
            index_name = self.config.vertex_autoindex
            return self.create_indexed_vertex(data,index_name,keys=None)
        message = self.message.create_vertex(data)
        return self.request.send(message)

    def get_vertex(self,_id):
        """Gets the vertex with the _id and returns the Response."""
        message = self.message.get_vertex(_id)
        return self.request.send(message)
        
    def update_vertex(self,_id,data):
        """Updates the vertex with the _id and returns the Response."""
        if self.config.autoindex is True:
            index_name = self.config.vertex_autoindex
            return self.update_indexed_vertex(_id,data,index_name,keys=None)
        message = self.message.update_vertex(_id,data)
        return self.request.send(message)

    def delete_vertex(self,_id):
        """Deletes a vertex with the _id and returns the Response."""
        message = self.message.delete_vertex(_id)
        return self.request.send(message)
        
    # Edge Proxy

    def create_edge(self,outV,label,inV,data={}): 
        """Creates a edge and returns the Response."""
        if self.config.autoindex is True:
            index_name = self.config.edge_autoindex
            return self.create_indexed_edge(outV,label,inV,data,index_name,keys=None)
        message = self.message.create_edge(outV,label,inV,data)
        return self.request.send(message)

    def get_edge(self,_id):
        """Gets the edge with the _id and returns the Response."""
        message = self.message.get_edge(_id)
        return self.request.send(message)
        
    def update_edge(self,_id,data):
        """Updates the edge with the _id and returns the Response."""
        if self.config.autoindex is True:
            index_name = self.config.edge_autoindex
            return self.update_indexed_edge(_id,data,index_name,keys=None)
        message = self.message.update_edge(_id, data)
        return self.request.send(message)

    def delete_edge(self,_id):
        """Deletes a edge with the _id and returns the Response."""
        message = self.message.delete_edge(_id)
        return self.request.send(message)

    # Vertex Container

    def outE(self,_id,label=None):
        """Return the outgoing edges of the vertex."""
        message = self.message.outE(_id,label)
        return self.request.send(message)

    def inE(self,_id,label=None):
        """Return the incoming edges of the vertex."""
        message = self.message.outE(_id,label)
        return self.request.send(message)

    def bothE(self,_id,label=None):
        """Return all incoming and outgoing edges of the vertex."""
        message = self.message.bothE(_id,label)
        return self.request.send(message)

    def outV(self,_id,label=None):
        """Return the out-adjacent vertices to the vertex."""
        message = self.message.outE(_id,label)
        return self.request.send(message)
        
    def inV(self,_id,label=None):
        """Return the in-adjacent vertices of the vertex."""
        message = self.message.outE(_id,label)
        return self.request.send(message)
        
    def bothV(self,_id,label=None):
        """Return all incoming- and outgoing-adjacent vertices of vertex."""
        message = self.message.outE(_id,label)
        return self.request.send(message)

    # Index Proxy - Vertex

    def create_vertex_index(self,index_name,*args,**kwds):
        """Creates a vertex index with the specified params."""
        message = self.message.create_vertex_index(index_name,*args,**kwds)
        resp = self.request.send(message)
        resp.set_index_name(index_name)        
        return resp

    def get_vertex_indices(self):
        """Returns a map of all the vertex indices."""
        message = self.message.get_vertex_indices()
        return self.request.send(message)

    def get_vertex_index(self,index_name):
        """Returns the vertex index with the index_name."""
        resp = self.get_vertex_indices()
        resp.results = self._get_index_results(index_name,resp)
        if resp.results:
            resp.set_index_name(index_name)
        return resp

    def delete_vertex_index(self,name): 
        """Deletes the vertex index with the index_name."""
        message = self.message.delete_vertex_index(name)
        return self.request.send(message)

    # Index Proxy - Edge

    def create_edge_index(self,index_name,*args,**kwds):
        """Creates a edge index with the specified params."""
        message = self.message.create_edge_index(index_name,*args,**kwds)
        resp = self.request.send(message)
        resp.set_index_name(index_name)
        return resp

    def get_edge_indices(self):
        """Returns a map of all the vertex indices."""
        message = self.message.get_edge_indices()
        return self.request.send(message)

    def get_edge_index(self,index_name):
        """Returns the edge index with the index_name."""
        resp = self.get_edge_indices()
        resp.results = self._get_index_results(index_name,resp)
        if resp.results:
            resp.set_index_name(index_name)
        return resp

    def delete_edge_index(self,name):
        """Deletes the edge index with the index_name."""
        message = self.message.delete_edge_index(name)
        return self.request.send(message)

    # Index Container - Vertex

    def put_vertex(self,name,key,value,_id):
        """Adds a vertex to the index with the index_name."""
        message = self.message.put_vertex(name,key,value,_id)
        return self.request.send(message)

    def lookup_vertex(self,name,key,value):
        """Returns the vertices indexed with the key and value."""
        message = self.message.lookup_vertex(name,key,value)
        return self.request.send(message)

    def query_vertex(self,name,params):
        """Returns the vertices for the index query."""
        message = self.message.query_vertex(name,params)
        return self.request.send(message)

    def remove_vertex(self,name,_id,key=None,value=None):
        """Removes a vertex from the index and returns the Response."""
        message = self.message.remove_vertex(name,_id,key,value)
        return self.request.send(message)

    # Index Container - Edge

    def put_edge(self,name,key,value,_id):
        """Adds an edge to the index and returns the Response."""
        message = self.message.put_edge(name,key,value,_id)
        return self.request.send(message)

    def lookup_edge(self,name,key,value):
        """Looks up an edge in the index and returns the Response."""
        message = self.message.lookup_edge(name,key,value)
        return self.request.send(message)

    def query_edge(self,name,params):
        """Queries for an edge in the index and returns the Response."""
        message = self.message.query_edge(name,params)
        return self.request.send(message)

    def remove_edge(self,name,_id,key=None,value=None):
        """Removes an edge from the index and returns the Response."""
        message = self.message.remove_edge(name,_id,key,value)
        return self.request.send(message)

    # Model Proxy - Vertex

    def create_indexed_vertex(self,data,index_name,keys=None):
        """Creates a vertex, indexes it, and returns the Response."""
        message = self.message.create_indexed_vertex(data,index_name,keys)
        return self.request.send(message)

    # Batch try...
    #def create_indexed_vertex(self,data,index_name,keys=None):
    #    """Creates a vertex, indexes it, and returns the Response."""
    #    batch = Neo4jBatch(self.resource)
    #    placeholder = batch.add(self.message.create_vertex(data))
    #    for key in keys:
    #        value = data.get(key)
    #        if value is None: continue
    #        batch.add(self.message.put_vertex(index_name,key,value,placeholder))
    #    resp = batch.send()
    #    #for result in resp.results:
    
    def update_indexed_vertex(self,_id,data,index_name,keys=None):
        """Updates an indexed vertex and returns the Response."""
        message = self.message.update_indexed_vertex(_id,data,index_name,keys)
        return self.request.send(message)

    # Model Proxy - Edge

    def create_indexed_edge(self,outV,label,inV,data,index_name,keys=None):
        """Creates a edge, indexes it, and returns the Response."""
        message = self.message.create_indexed_edge(outV,label,inV,data,index_name,keys)
        return self.request.send(message)

    def update_indexed_edge(self,_id,data,index_name,keys=None):
        """Updates an indexed edge and returns the Response."""
        message = self.message.update_indexed_edge(_id,data,index_name,keys)
        return self.request.send(message)

    # Utils

    def warm_cache(self):
        """Warms the server cache by loading elements into memory."""
        message = self.message.warm_cache()
        return self.request.send(message)

    # Private 

    def _get_scripts_file(self,file_name):
        """Returns the full file path for the scripts file."""
        dir_name = os.path.dirname(__file__)
        file_path = get_file_path(dir_name,file_name)
        return file_path

    def _get_index_results(self,index_name,resp):
        """Returns the index from a map of indicies."""
        if resp.content and index_name in resp.content:
            result = resp.content[index_name]
            return Neo4jResult(result, self.config)



