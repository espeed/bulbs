# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""

Bulbs supports pluggable backends. These are the abstract base classes that 
provides the server-client interface. Implement these to create a new client. 

"""
import inspect

from bulbs.utils import json, build_path, get_file_path, get_logger
from bulbs.registry import Registry
from bulbs.config import DEBUG


log = get_logger(__name__)

# TODO: Consider making these real Python Abstract Base Classes (import abc)            

class Result(object):
    """
    Abstract base class for a single result, not a list of results.  

    :param result: The raw result.
    :type result: dict

    """

    def __init__(self, result):
        #: The raw result.
        self.raw = result
        
        #: The data in the result.
        self.data = None

    def get_id(self):
        """Returns the element ID."""
        raise NotImplementedError
    
    def get_type(self):
        """Returns vertex or edge."""
        raise NotImplementedError

    def get_uri(self):
        """Returns the element URI."""
        raise NotImplementedError

    def get_outV(self):
        """Returns the ID of the edge's outgoing vertex (start node)."""
        raise NotImplementedError

    def get_inV(self):
        """Returns the ID of the edge's incoming vertex (end node)."""
        raise NotImplementedError

    def get_label(self):
        """Returns the edge label (relationship type)."""
        raise NotImplementedError

    def get(self, attribute):
        """
        Returns the value of a client-specific attribute.

        :param attribute: Name of the attribute:
        :type attribute: str

        :rtype: str

        """
        return self.raw[attribute]


class Response(object):
    """
    Abstract base class for the response returned by the request.
    
    :param response: The raw response; its type will depend on the Client.

    """

    result_class = Result

    def __init__(self,  response, config):
        self.handle_response(response)

        #: A dict containing the content returned in the response.
        self.content = self.get_content(response)

        #: The Result object or a generator of Result objects, along with the count.
        self.results, self.total_size = self.get_results()

        #: The raw response returned by the request.
        self.raw = self._maybe_get_raw(response, config)

    def _maybe_get_raw(self,response, config):
        # don't store raw response in production else you'll bloat the obj
        if config.log_level == DEBUG:
            return response

    def handle_response(self, response):
        """Check the server response and raise exceptions if needed."""
        raise NotImplementedError

    def get_content(self, response):
        """Return a dict containing the content returned in the response."""
        raise NotImplementedError

    def get_results(self):
        """Return a Result object or a generator of Result objects."""
        raise NotImplementedError

    def get(self, attribute):
        """Return a client-specific attribute."""
        return self.content[attribute]

    def one(self):
        """Returns one result"""
        # If you're using this utility, that means the results attribute in the 
        # Response object should always contain a single result object,
        # not multiple items. But gremlin returns all results as a list
        # even if the list contains only one element. And the Response class
        # converts all lists to a generator of Result objects. Thus in that case,
        # we need to grab the single Result object out of the list/generator.
        if self.total_size > 1:
            log.error('resp.results contains more than one item.')
            raise ValueError
        if inspect.isgenerator(self.results):
            result = next(self.results)
        else:
            result = self.results
        return result
        


class Client(object):
    """
    Abstract base class for a server client.

    :param config: Config object containing instance-specific configuration. 

    """

    def __init__(self, config):
        #: Config object containing instance-specific configuration. 
        self.config = config

        #: Registry object to hold classes, proxies, indices, and scripts.
        self.registery = Registry()

    # Gremlin

    def gremlin(self, script, params=None): 
        """Executes a Gremlin script and returns the Response."""
        raise NotImplementedError 

    # Vertex Proxy

    def create_vertex(self, data):
        """Creates a vertex and returns the Response."""
        raise NotImplementedError
    
    def get_vertex(self, _id):
        """Gets the vertex with the _id and returns the Response."""
        raise NotImplementedError 

    def update_vertex(self, _id, data):
        """Updates the vertex with the _id and returns the Response."""
        raise NotImplementedError 

    def delete_vertex(self, _id):
        """Deletes a vertex with the _id and returns the Response."""
        raise NotImplementedError 

    # Edge Proxy

    def create_edge(self, outV, label, inV, data={}): 
        """Creates a edge and returns the Response."""
        raise NotImplementedError 

    def get_edge(self, _id):
        """Gets the edge with the _id and returns the Response."""
        raise NotImplementedError 

    def update_edge(self, _id, data):
        """Updates the edge with the _id and returns the Response."""
        raise NotImplementedError 

    def delete_edge(self, _id):
        """Deletes a edge with the _id and returns the Response."""
        raise NotImplementedError 

    # Vertex Container

    def outE(self, _id, label=None):
        """Returns the outgoing edges of the vertex."""
        raise NotImplementedError 

    def inE(self, _id, label=None):
        """Returns the incoming edges of the vertex."""
        raise NotImplementedError 

    def bothE(self, _id, label=None):
        """Returns the outgoing and incoming edges of the vertex."""
        raise NotImplementedError 

    def outV(self, _id, label=None):
        """Returns the adjacent outgoing vertices of the vertex."""
        raise NotImplementedError 

    def inV(self, _id, label=None):
        """Returns the adjacent incoming vertices of the vertex."""
        raise NotImplementedError 

    def bothV(self, _id, label=None):
        """Returns the adjacent outgoing and incoming vertices of the vertex."""
        raise NotImplementedError 

    # Index Proxy - Vertex

    def create_vertex_index(self, params):
        """Creates a vertex index with the specified params."""
        raise NotImplementedError 

    def get_vertex_index(self, index_name):
        """Returns the vertex index with the index_name."""
        raise NotImplementedError 
        
    def delete_vertex_index(self, index_name): 
        """Deletes the vertex index with the index_name."""
        raise NotImplementedError 

    # Index Proxy - Edge

    def create_edge_index(self, params):
        """Creates a edge index with the specified params."""
        raise NotImplementedError 

    def get_edge_index(self, index_name):
        """Returns the edge index with the index_name."""
        raise NotImplementedError 
        
    def delete_edge_index(self, index_name): 
        """Deletes the edge index with the index_name."""
        raise NotImplementedError 
    
    # Index Container - Vertex

    def put_vertex(self, index_name, key, value, _id):
        """Adds a vertex to the index with the index_name."""
        raise NotImplementedError 

    def lookup_vertex(self, index_name, key, value):
        """Returns the vertices indexed with the key and value."""
        raise NotImplementedError 

    def query_vertex(self, index_name, params):
        """Returns the vertices for the index query."""
        raise NotImplementedError 

    def remove_vertex(self, index_name, _id, key=None, value=None):
        """Removes a vertex from the index and returns the Response."""
        raise NotImplementedError 

    # Index Container - Edge

    def put_edge(self, index_name, key, value, _id):
        """Adds an edge to the index and returns the Response."""
        raise NotImplementedError 

    def lookup_edge(self, index_name, key, value):
        """Looks up an edge in the index and returns the Response."""
        raise NotImplementedError 

    def query_edge(self, index_name, params):
        """Queries for an edge in the index and returns the Response."""
        raise NotImplementedError 

    def remove_edge(self, index_name, _id, key=None, value=None):
        """Removes an edge from the index and returns the Response."""
        raise NotImplementedError 

    # Model Proxy - Vertex

    def create_indexed_vertex(self, data, index_name, keys=None):
        """Creates a vertex, indexes it, and returns the Response."""
        raise NotImplementedError 

    def update_indexed_vertex(self, _id, data, index_name, keys=None):
        """Updates an indexed vertex and returns the Response."""
        raise NotImplementedError 

    # Model Proxy - Edge

    def create_indexed_edge(self, data, index_name, keys=None):
        """Creates a edge, indexes it, and returns the Response."""
        raise NotImplementedError 

    def update_indexed_edge(self, _id, data, index_name, keys=None):
        """Updates an indexed edge and returns the Response."""
        raise NotImplementedError 
    
    # Utils

    def warm_cache(self):
        """Warms the server cache by loading elements into memory."""
        raise NotImplementedError 

        
