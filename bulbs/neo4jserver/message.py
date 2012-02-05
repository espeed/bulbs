# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Build the messages sent in single and batch requests.

"""
import re
from bulbs.utils import build_path
from bulbs.rest import GET, PUT, POST, DELETE


vertex_path = "node"
edge_path = "relationship"
index_path = "index"
gremlin_path = "ext/GremlinPlugin/graphdb/execute_script"
cypher_path = "ext/CypherPlugin/graphdb/execute_query"


class Message(object):
    """Request message..."""

    def __init__(self, config, scripts):
        self.config = config
        self.scripts = scripts

    # Gremlin

    def gremlin(self,script,params):
        """Returns the a Gremlin Message ready to be executed.""" 
        path = gremlin_path
        params = dict(script=script,params=params)
        return POST, path, params

    # Cypher

    def cypher(self,query,params=None):
        """Executes a Cypher query and returns the Response."""
        path = cypher_path
        params = dict(query=query,params=params)
        return POST, path, params 

    # Vertex Proxy

    def create_vertex(self,data):
        """Creates a vertex and returns the Response."""
        path = vertex_path
        params = self._remove_null_values(data)
        return POST, path, params

    def get_vertex(self,_id):
        """Gets the vertex with the _id and returns the Response."""
        path = self._build_vertex_path(_id)
        params = None
        return GET, path, params
 
    def update_vertex(self,_id,data):
        """Updates the vertex with the _id and returns the Response."""
        path = self._build_vertex_path(_id,"properties")
        params = self._remove_null_values(data)
        return PUT, path, params

    def delete_vertex(self,_id):
        """Deletes a vertex with the _id and returns the Response."""
        script = self.scripts.get("delete_vertex")
        params = dict(_id=_id)
        return self.gremlin(script,params)
        
    # Edge Proxy

    def create_edge(self,outV,label,inV,data={}): 
        """Creates a edge and returns the Response."""
        data = self._remove_null_values(data)
        inV_uri = self._build_vertex_uri(inV)
        path = build_path(vertex_path,outV,"relationships")
        params = {'to':inV_uri,'type':label, 'data':data}
        return POST, path, params
        
    def get_edge(self,_id):
        """Gets the edge with the _id and returns the Response."""
        path = build_path(edge_path,_id)
        params = None
        return GET, path, params
        
    def update_edge(self,_id,data):
        """Updates the edge with the _id and returns the Response."""
        path = build_path(edge_path,_id,"properties")
        params = self._remove_null_values(data)
        return PUT, path, params

    def delete_edge(self,_id):
        """Deletes a edge with the _id and returns the Response."""
        path = build_path(edge_path,_id)
        params = None
        return DELETE, path, params

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

    # Index Proxy - Vertex

    def create_vertex_index(self,index_name,*args,**kwds):
        """Creates a vertex index with the specified params."""
        index_type = kwds.pop("index_type","exact")
        provider = kwds.pop("provider","lucene")
        #keys = kwds.pop("keys",None)
        #config = {'type':index_type,'provider':provider,'keys':str(keys)}
        config = {'type':index_type,'provider':provider}
        path = build_path(index_path,"node")
        params = dict(name=index_name,config=config)
        return POST, path, params

    def get_vertex_indices(self):
        """Returns a map of all the vertex indices."""
        path = build_path(index_path,"node")
        params = None
        return GET, path, params

    def get_vertex_index(self,index_name):
        """Returns the vertex index with the index_name."""
        # This is implemented in the Resource class, but could be done in Gremlin.
        raise NotImplementedError

    def delete_vertex_index(self,name): 
        """Deletes the vertex index with the index_name."""
        path = build_path(index_path,"node",name)
        params = None
        return DELETE, path, params

    # Index Proxy - Edge

    def create_edge_index(self,index_name,*args,**kwds):
        """Creates a edge index with the specified params."""
        path = build_path(index_path,edge_path)
        params = dict(name=index_name)
        return POST, path, params

    def get_edge_indices(self):
        """Returns a map of all the vertex indices."""
        path = build_path(index_path,edge_path)
        params = None
        return GET, path, params

    def get_edge_index(self,index_name):
        """Returns the edge index with the index_name."""
        # This is implemented in the Resource class, but could be done in Gremlin.
        raise NotImplementedError

    def delete_edge_index(self,name):
        """Deletes the edge index with the index_name."""
        path = build_path(index_path,edge_path,name)
        params = None
        return DELETE, path, params

    # Index Container - Vertex

    def put_vertex(self,name,key,value,_id):
        """Adds a vertex to the index with the index_name."""
        uri = "%s/%s/%d" % (self.config.root_uri,"node",_id)
        path = build_path(index_path,"node",name)
        params = dict(key=key,value=value,uri=uri)
        return POST, path, params

    def lookup_vertex(self,name,key,value):
        """Returns the vertices indexed with the key and value."""
        path = build_path(index_path,"node",name,key,value)
        params = None
        return GET, path, params

    def query_vertex(self,name,params):
        """Returns the vertices for the index query."""
        path = build_path(index_path,"node",name)
        params = params
        return GET, path, params

    def remove_vertex(self,name,_id,key=None,value=None):
        """Removes a vertex from the index and returns the Response."""
        path = build_path("node",name,key,value,_id)
        params = None
        return DELETE, path, params

    # Index Container - Edge

    def put_edge(self,name,key,value,_id):
        """Adds an edge to the index and returns the Response."""
        uri = "%s/%s/%d" % (self.config.root_uri,edge_path,_id)
        path = build_path(index_path,edge_path,name)
        params = dict(key=key,value=value,uri=uri)
        return POST, path, params

    def lookup_edge(self,name,key,value):
        """Looks up an edge in the index and returns the Response."""
        path = build_path(index_path,edge_path,name,key,value)
        params = None
        return GET, path, params

    def query_edge(self,name,params):
        """Queries for an edge in the index and returns the Response."""
        path = build_path(index_path,edge_path,name)
        params = params
        return GET, path, params

    def remove_edge(self,name,_id,key=None,value=None):
        """Removes an edge from the index and returns the Response."""
        path = build_path(edge_path,name,key,value,_id)
        params = None
        return DELETE, path, params

    # Model Proxy - Vertex

    def create_indexed_vertex(self,data,index_name,keys=None):
        """Creates a vertex, indexes it, and returns the Response."""
        data = self._remove_null_values(data)
        params = dict(data=data,index_name=index_name,keys=keys)
        script = self.scripts.get("create_indexed_vertex")
        return self.gremlin(script,params)
        
    def update_indexed_vertex(self,_id,data,index_name,keys=None):
        """Updates an indexed vertex and returns the Response."""
        data = self._remove_null_values(data)
        params = dict(_id=_id,data=data,index_name=index_name,keys=keys)
        script = self.scripts.get("update_indexed_vertex")
        return self.gremlin(script,params)

    # Model Proxy - Edge

    def create_indexed_edge(self,outV,label,inV,data,index_name,keys=None):
        """Creates a edge, indexes it, and returns the Response."""
        data = self._remove_null_values(data)
        edge_params = dict(outV=outV,label=label,inV=inV)
        params = dict(data=data,index_name=index_name,keys=keys)
        params.update(edge_params)
        script = self.scripts.get("create_indexed_edge")
        return self.gremlin(script,params)

    def update_indexed_edge(self,_id,data,index_name,keys=None):
        """Updates an indexed edge and returns the Response."""
        data = self._remove_null_values(data)
        params = dict(_id=_id,data=data,index_name=index_name,keys=keys)
        script = self.scripts.get("update_indexed_edge")
        return self.gremlin(script,params)

    # Utils

    def warm_cache(self):
        """Warms the server cache by loading elements into memory."""
        script = self.scripts.get('warm_cache')
        return self.gremlin(script,params=None)

    # Private 

    def _remove_null_values(self,data):
        """Removes null property values because they aren't valid in Neo4j."""
        # Neo4j Server uses PUTs to overwrite all properties so no need
        # to worry about deleting props that are being set to null.
        clean_data = [(k, v) for k, v in data.items() if v is not None]
        return dict(clean_data)

    def _placeholder(self,_id):
        pattern = "^{.*}$"
        match = re.search(pattern,str(_id))
        if match:
            placeholder = match.group()
            return placeholder

    def _build_vertex_path(self,_id,*args):
        # if the _id is a placeholder, return the placeholder;
        # othewise, return a normal vertex path
        placeholder = self._placeholder(_id) 
        if placeholder:
            segments = [placeholder]
        else:
            segments = [vertex_path,_id]
        segments = segments + list(args)
        return build_path(*segments)
        
    def _build_vertex_uri(self,_id,*args):
        placeholder = self._placeholder(_id) 
        if placeholder:
            return placeholder
        root_uri = self.config.root_uri.rstrip("/")
        segments = [vertex_path, _id] + list(args)
        path = build_path(*segments)
        uri = "%s/%s" % (root_uri, path)
        return uri

    def _build_edge_path(self,_id):
        # if the _id is a placeholder, return the placeholder;
        # othewise, return a normal edge path
        return self._placeholder(_id) or build_path(edge_path,_id)

    def _build_edge_uri(self,_id):
        pass





