# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Bulbs supports pluggable clients. This is the Rexster client.

"""
from bulbs.config import Config, DEBUG
from bulbs.registry import Registry
from bulbs.utils import get_logger

# specific to this client
from bulbs.json import JSONTypeSystem
from bulbs.base import Client, Response, Result 
from bulbs.rest import Request, RESPONSE_HANDLERS
from bulbs.groovy import GroovyScripts

from bulbs.utils import json, build_path, get_file_path, urlsplit, coerce_id


##### Titan

from bulbs.rexster.client import RexsterClient, \
    RexsterResponse, RexsterResult

# The default URIs
TITAN_URI = "http://localhost:8182/graphs/graph"

# The logger defined in Config
log = get_logger(__name__)

# Rexster resource paths
# TODO: local path vars would be faster
vertex_path = "vertices"
edge_path = "edges"
index_path = "indices"
gremlin_path = "tp/gremlin"
transaction_path = "tp/batch/tx"
multi_get_path = "tp/batch"
key_index_path = "keyindices"

class TitanResult(RexsterResult):
    """
    Container class for a single result, not a list of results.

    :param result: The raw result.
    :type result: dict

    :param config: The client Config object.
    :type config: Config 

    :ivar raw: The raw result.
    :ivar data: The data in the result.

    """
    pass


class TitanResponse(RexsterResponse):
    """
    Container class for the server response.

    :param response: httplib2 response: (headers, content).
    :type response: tuple

    :param config: Config object.
    :type config: bulbs.config.Config

    :ivar config: Config object.
    :ivar headers: httplib2 response headers, see:
        http://httplib2.googlecode.com/hg/doc/html/libhttplib2.html
    :ivar content: A dict containing the HTTP response content.
    :ivar results: A generator of RexsterResult objects, a single RexsterResult object, 
        or None, depending on the number of results returned.
    :ivar total_size: The number of results returned.
    :ivar raw: Raw HTTP response. Only set when log_level is DEBUG.

    """
    result_class = TitanResult



class TitanRequest(Request):
    """Makes HTTP requests to Rexster and returns a RexsterResponse.""" 
    
    response_class = TitanResponse


data_type = dict(string="String", 
                 integer="Integer", 
                 geoshape="Geoshape",)


class TitanClient(RexsterClient):
    """
    Low-level client that sends a request to Titan and returns a response.

    :param config: Optional Config object. Defaults to default Config.
    :type config: bulbs.config.Config

    :cvar default_uri: Default URI for the database.
    :cvar request_class: Request class for the Client.

    :ivar config: Config object.
    :ivar registry: Registry object.
    :ivar scripts: GroovyScripts object.  
    :ivar type_system: JSONTypeSystem object.
    :ivar request: TitanRequest object.

    Example:

    >>> from bulbs.titan import TitanClient
    >>> client = TitanClient()
    >>> script = client.scripts.get("get_vertices")
    >>> response = client.gremlin(script, params=None)
    >>> result = response.results.next()

    """ 
    #: Default URI for the database.
    default_uri = TITAN_URI
    request_class = TitanRequest



    def __init__(self, config=None, db_name=None):
        super(TitanClient, self).__init__(config, db_name)

        # override so Rexster create_vertex() method doesn't try to index
        self.config.autoindex = False 


    # GET 

    # these could replace the Rexster Gremlin version of these methods
    def outV(self, _id, label=None, start=None, limit=None, properties=None):
        path = build_path(vertex_path, _id, "out")
        params = build_params(_label=label, _limit=limit, _properties=properties)
        return self.request.get(path, params)
    
    def inV(self, _id, label=None, start=None, limit=None, properties=None):
        path = build_path(vertex_path, _id, "in")
        params = build_params(_label=label, _limit=limit, _properties=properties)
        return self.request.get(path, params)

    def bothV(self, _id, label=None, start=None, limit=None, properties=None):
        path = build_path(vertex_path, _id, "both")
        params = build_params(_label=label, _limit=limit, _properties=properties)
        return self.request.get(path, params)

    def outV_count(self, _id, label=None, start=None, limit=None, properties=None):
        path = build_path(vertex_path, _id, "outCount")
        params = build_params(_label=label, _limit=limit, _properties=properties)
        return self.request.get(path, params)

    def inV_count(self, _id, label=None, start=None, limit=None, properties=None):
        path = build_path(vertex_path, _id, "inCount")
        params = build_params(_label=label, _limit=limit, _properties=properties)
        return self.request.get(path, params)

    def bothV_count(self, _id, label=None, start=None, limit=None, properties=None):
        path = build_path(vertex_path, _id, "bothCount")
        params = build_params(_label=label, _limit=limit, _properties=properties)
        return self.request.get(path, params)

    def outV_ids(self, _id, label=None, start=None, limit=None, properties=None):
        path = build_path(vertex_path, _id, "outIds")
        params = build_params(_label=label, _limit=limit, _properties=properties)
        return self.request.get(path, params)

    def inV_ids(self, _id, label=None, start=None, limit=None, properties=None):
        path = build_path(vertex_path, _id, "inIds")
        params = build_params(_label=label, _limit=limit, _properties=properties)
        return self.request.get(path, params)

    def bothV_ids(self, _id, label=None, start=None, limit=None, properties=None):
        path = build_path(vertex_path, _id, "bothIds")
        params = build_params(_label=label, _limit=limit, _properties=properties)
        return self.request.get(path, params)

    def outE(self, _id, label=None, start=None, limit=None, properties=None):
        path = build_path(vertex_path, _id, "outE")
        params = build_params(_label=label, _limit=limit, _properties=properties)
        return self.request.get(path, params)
    
    def inE(self, _id, label=None, start=None, limit=None, properties=None):
        path = build_path(vertex_path, _id, "inE")
        params = build_params(_label=label, _limit=limit, _properties=properties)
        return self.request.get(path, params)

    def bothE(self, _id, label=None, start=None, limit=None, properties=None):
        path = build_path(vertex_path, _id, "bothE")
        params = build_params(_label=label, _limit=limit, _properties=properties)
        return self.request.get(path, params)

    # Key Indices

    # Titan-Specific Index Methods

    # https://github.com/thinkaurelius/titan/wiki/Indexing-Backend-Overview                       
    # https://github.com/thinkaurelius/titan/wiki/Type-Definition-Overview

    def create_edge_label(self, label):
        # TODO: custom gremlin method
        pass

    def create_vertex_property_key():
        # TODO: custom gremlin method
        pass

    def create_edge_property_key():
        # TODO: custom gremlin method
        pass
    
    def create_vertex_key_index(self, key):
        path = build_path(key_index_path, "vertex", key)
        params = None
        return self.request.post(path, params)

    def create_edge_key_index(self, key):
        path = build_path(key_index_path, "edge", key)
        params = None
        return self.request.post(path, params)

    def get_vertex_keys(self):
        path = build_path(key_index_path, "vertex")
        params = None
        return self.request.get(path, params)

    def get_edge_keys(self):
        path = build_path(key_index_path, "edge")
        params = None
        return self.request.get(path, params)

    def get_all_keys(self):
        path = key_index_path
        params = None
        return self.request.get(path, params)


    # Index Proxy - General

    def get_all_indices(self):
        """Returns a list of all the element indices."""
        raise NotImplementedError

    def get_index(self, name):
        raise NotImplementedError

    def delete_index(self, name): 
        raise NotImplementedError
    
    # Index Proxy - Vertex

    def create_vertex_index(self, index_name, *args, **kwds):
        """
        Creates a vertex index with the specified params.

        :param index_name: Name of the index to create.
        :type index_name: str

        :rtype: TitanResponse

        """
        raise NotImplementedError

    def get_vertex_index(self, index_name):
        """
        Returns the vertex index with the index_name.

        :param index_name: Name of the index.
        :type index_name: str

        :rtype: TitanResponse

        """
        raise NotImplementedError

    def get_or_create_vertex_index(self, index_name, index_params=None):
        raise NotImplementedError
        
    def delete_vertex_index(self, name): 
        """
        Deletes the vertex index with the index_name.

        :param index_name: Name of the index.
        :type index_name: str

        :rtype: TitanResponse

        """
        raise NotImplementedError

    # Index Proxy - Edge
    # Titan does NOT support edge indices

    def create_edge_index(self, name, *args, **kwds):
        raise NotImplementedError
        
    def get_edge_index(self, name):
        """
        Returns the edge index with the index_name.

        :param index_name: Name of the index.
        :type index_name: str

        :rtype: TitanResponse

        """
        raise NotImplementedError
        
    def get_or_create_edge_index(self, index_name, index_params=None):
        raise NotImplementedError

    def delete_edge_index(self, name):
        raise NotImplementedError

    # Index Container - Vertex

    def put_vertex(self, index_name, key, value, _id):
        # Titan only supports automatic indices
        raise NotImplementedError

    def lookup_vertex(self, index_name, key, value):
        """
        Returns the vertices indexed with the key and value.

        :param index_name: Name of the index.
        :type index_name: str

        :param key: Name of the key.
        :type key: str

        :param value: Value of the key.
        :type value: str

        :rtype: TitanResponse

        """
        # NOTE: this is different than Rexster's version
        # it uses vertex_path instead of index_path, and 
        # index_name is N/A
        # Keeping method interface the same for practical reasons so
        # index_name will be ignored, any value will work.
        path = build_path(vertex_path)
        params = dict(key=key,value=value)
        return self.request.get(path,params)

    def query_vertex(self, index_name, params):
        """Queries for an vertex in the index and returns the Response."""
        path = build_path(index_path,index_name)
        return self.request.get(path,params)

    def remove_vertex(self,index_name,_id,key=None,value=None):
        # Titan only supports automatic indices
        raise NotImplementedError

    # Index Container - Edge 
    # Titan does NOT support edge indices

    def put_edge(self, index_name, key, value, _id):
        raise NotImplementedError

    def lookup_edge(self, index_name, key, value):
        """
        Looks up an edge in the index and returns the Response.
        """
        # NOTE: this is different than Rexster's version
        # it uses edge_path instead of index_path, and 
        # index_name is N/A
        # Keeping method interface the same for practical reasons so
        # index_name will be ignored, any value will work.
        #path = build_path(edge_path)
        #params = dict(key=key,value=value)
        #return self.request.get(path,params)
        raise NotImplementedError

    def query_edge(self, index_name, params):
        """Queries for an edge in the index and returns the Response."""
        raise NotImplementedError

    def remove_edge(self, index_name, _id, key=None, value=None):
        raise NotImplementedError
    
    # Model Proxy - Vertex

    def create_indexed_vertex(self, data, index_name, keys=None):
        """
        Creates a vertex, indexes it, and returns the Response.

        :param data: Property data.
        :type data: dict

        :param index_name: Name of the index.
        :type index_name: str

        :param keys: Property keys to index.
        :type keys: list

        :rtype: TitanResponse

        """
        return self.create_vertex(data)
    
    def update_indexed_vertex(self, _id, data, index_name, keys=None):
        """
        Updates an indexed vertex and returns the Response.

        :param index_name: Name of the index.
        :type index_name: str

        :param data: Property data.
        :type data: dict

        :param index_name: Name of the index.
        :type index_name: str

        :param keys: Property keys to index.
        :type keys: list

        :rtype: TitanResponse

        """
        return self.update_vertex(_id, data)

    # Model Proxy - Edge

    def create_indexed_edge(self, outV, label, inV, data, index_name, keys=None):
        """
        Creates a edge, indexes it, and returns the Response.

        :param outV: Outgoing vertex ID.
        :type outV: int

        :param label: Edge label.
        :type label: str

        :param inV: Incoming vertex ID.
        :type inV: int

        :param data: Property data.
        :type data: dict

        :param index_name: Name of the index.
        :type index_name: str

        :param keys: Property keys to index. Defaults to None (indexes all properties).
        :type keys: list

        :rtype: TitanResponse

        """
        return self.create_edge(outV, label, inV, data)
        
    def update_indexed_edge(self, _id, data, index_name, keys=None):
        """
        Updates an indexed edge and returns the Response.

        :param _id: Edge ID.
        :type _id: int

        :param data: Property data.
        :type data: dict

        :param index_name: Name of the index.
        :type index_name: str

        :param keys: Property keys to index. Defaults to None (indexes all properties).
        :type keys: list

        :rtype: TitanResponse

        """
        return self.update_edge(_id, data)



# Utils

def build_params(**kwds):
    # Rexster isn't liking None param values
    params = dict()
    for key in kwds:
        value = kwds[key]
        if value is not None:
            params[key] = value
    return params
