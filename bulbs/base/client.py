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

from bulbs.config import Config, DEBUG
from bulbs.registry import Registry
from bulbs.utils import get_logger

from .typesystem import TypeSystem

SERVER_URI = "http://localhost"

log = get_logger(__name__)

# TODO: Consider making these real Python Abstract Base Classes (import abc)            

class Request(object):

    def __init__(self, config, content_type):
        """
        Initializes a client object.

        :param root_uri: the base URL of Rexster.

        """
        self.config = config
        self.content_type = content_type
        self._initialize()

    def _initialize(self):
        pass

class Result(object):
    """
    Abstract base class for a single result, not a list of results.  

    :param result: The raw result.
    :type result: dict

    :param config: The graph Config object.
    :type config: Config 

    :ivar raw: The raw result.
    :ivar data: The data in the result.

    """

    def __init__(self, result, config):
        self.config = config

        # The raw result.
        self.raw = result
        
        # The data in the result.
        self.data = None

    def get_id(self):
        """
        Returns the element ID.

        :rtype: int

        """
        raise NotImplementedError
    
    def get_type(self):
        """
        Returns the element's base type, either "vertex" or "edge".

        :rtype: str

        """
        raise NotImplementedError

    def get_data(self):
        """
        Returns the element's property data.

        :rtype: dict

        """
        raise NotImplementedError

    def get_uri(self):
        """
        Returns the element URI.

        :rtype: str

        """
        raise NotImplementedError

    def get_outV(self):
        """
        Returns the ID of the edge's outgoing vertex (start node).

        :rtype: int

        """
        raise NotImplementedError

    def get_inV(self):
        """
        Returns the ID of the edge's incoming vertex (end node).

        :rtype: int

        """
        raise NotImplementedError

    def get_label(self):
        """
        Returns the edge label (relationship type).

        :rtype: str

        """
        raise NotImplementedError

    def get_index_name(self):
        """
        Returns the index name.

        :rtype: str

        """
        raise NotImplementedError
   
    def get_index_class(self):
        """
        Returns the index class, either "vertex" or "edge".

        :rtype: str

        """
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
    
    :param response: The raw response.
    :type response: Depends on Client.

    :param config: Config object.
    :type config: bulbs.config.Config

    :ivar config: Config object.
    :ivar headers: Response headers.
    :ivar content: A dict containing the response content.
    :ivar results: A generator of Neo4jResult objects, a single Neo4jResult object, 
        or None, depending on the number of results returned.
    :ivar total_size: The number of results returned.
    :ivar raw: Raw HTTP response. Only set when log_level is DEBUG.

    """
    result_class = Result

    def __init__(self,  response, config):
        self.config = config
        self.handle_response(response)
        self.headers = self.get_headers(response)
        self.content = self.get_content(response)
        self.results, self.total_size = self.get_results()
        self.raw = self._maybe_get_raw(response, config)

    def _maybe_get_raw(self,response, config):
        """Returns the raw response if in DEBUG mode."""
        # don't store raw response in production else you'll bloat the obj
        if config.log_level == DEBUG:
            return response

    def handle_response(self, response):
        """
        Check the server response and raise exception if needed.
        
        :param response: Raw server response.
        :type response: Depends on Client.

        :rtype: None

        """
        raise NotImplementedError

    def get_headers(self, response):
        """
        Returns a dict containing the headers from the response.

        :param response: Raw server response.
        :type response: tuple
        
        :rtype: httplib2.Response

        """
        raise NotImplementedError

    def get_content(self, response):
        """
        Returns a dict containing the content from the response.
        
        :param response: Raw server response.
        :type response: tuple
        
        :rtype: dict or None

        """
        raise NotImplementedError

    def get_results(self):
        """
        Returns the results contained in the response.

        :return:  A tuple containing two items: 1. Either a generator of Neo4jResult objects, 
                  a single Neo4jResult object, or None, depending on the number of results 
                  returned; 2. An int representing the number results returned.
        :rtype: tuple

        """
        raise NotImplementedError

    def get(self, attribute):
        """Return a client-specific attribute."""
        return self.content[attribute]

    def one(self):
        """
        Returns one result or raises an error if there is more than one result.

        :rtype: Result

        """
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
    Abstract base class for the low-level server client.

    :param config: Optional Config object. Defaults to default Config.
    :type config: bulbs.config.Config

    :cvar default_uri: Default URI for the database.
    :cvar request_class: Request class for the Client.

    :ivar config: Config object.
    :ivar registry: Registry object.
    :ivar type_system: TypeSystem object.
    :ivar request: Request object.

    Example:

    >>> from bulbs.neo4jserver import Neo4jClient
    >>> client = Neo4jClient()
    >>> script = client.scripts.get("get_vertices")
    >>> response = client.gremlin(script, params=None)
    >>> result = response.results.next()


    """
    default_uri = SERVER_URI
    request_class = Request


    def __init__(self, config=None):
        self.config = config or Config(self.default_uri)
        self.registry = Registry(self.config)
        self.type_system = TypeSystem()
        self.request = self.request_class(self.config, self.type_system.content_type)

    # Vertex Proxy

    def create_vertex(self, data):
        """
        Creates a vertex and returns the Response.

        :param data: Property data.
        :type data: dict

        :rtype: Response

        """
        raise NotImplementedError
    
    def get_vertex(self, _id):
        """
        Gets the vertex with the _id and returns the Response.

        :param data: Vertex ID.
        :type data: int

        :rtype: Response

        """
        raise NotImplementedError 

    def get_all_vertices(self):
        """
        Returns a Response containing all the vertices in the Graph.

        :rtype: Response

        """
        raise NotImplementedError 

    def update_vertex(self, _id, data):
        """
        Updates the vertex with the _id and returns the Response.

        :param _id: Vertex ID.
        :type _id: dict

        :param data: Property data.
        :type data: dict

        :rtype: Response

        """
        raise NotImplementedError 

    def delete_vertex(self, _id):
        """
        Deletes a vertex with the _id and returns the Response.

        :param _id: Vertex ID.
        :type _id: dict

        :rtype: Response

        """
        raise NotImplementedError 

    # Edge Proxy

    def create_edge(self, outV, label, inV, data=None):
        """
        Creates a edge and returns the Response.
        
        :param outV: Outgoing vertex ID.
        :type outV: int

        :param label: Edge label.
        :type label: str

        :param inV: Incoming vertex ID.
        :type inV: int

        :param data: Property data.
        :type data: dict or None

        :rtype: Response

        """
        raise NotImplementedError 

    def get_edge(self, _id):
        """
        Gets the edge with the _id and returns the Response.

        :param data: Edge ID.
        :type data: int

        :rtype: Response

        """
        raise NotImplementedError 

    def get_all_edges(self):
        """
        Returns a Response containing all the edges in the Graph.

        :rtype: Response

        """
        raise NotImplementedError 

    def update_edge(self, _id, data):
        """
        Updates the edge with the _id and returns the Response.

        :param _id: Edge ID.
        :type _id: dict

        :param data: Property data.
        :type data: dict

        :rtype: Response

        """
        raise NotImplementedError 

    def delete_edge(self, _id):
        """
        Deletes a edge with the _id and returns the Response.

        :param _id: Edge ID.
        :type _id: dict

        :rtype: Response

        """
        raise NotImplementedError 

    # Vertex Container

    def outE(self, _id, label=None):
        """
        Returns the outgoing edges of the vertex.

        :param _id: Vertex ID.
        :type _id: dict

        :param label: Optional edge label. Defaults to None.
        :type label: str

        :rtype: Response
        
        """
        raise NotImplementedError 

    def inE(self, _id, label=None):
        """
        Returns the incoming edges of the vertex.

        :param _id: Vertex ID.
        :type _id: dict

        :param label: Optional edge label. Defaults to None.
        :type label: str

        :rtype: Response

        """
        raise NotImplementedError 

    def bothE(self, _id, label=None):
        """
        Returns the incoming and outgoing edges of the vertex.

        :param _id: Vertex ID.
        :type _id: dict

        :param label: Optional edge label. Defaults to None.
        :type label: str

        :rtype: Response
        
        """
        raise NotImplementedError 

    def outV(self, _id, label=None):
        """
        Returns the out-adjacent vertices of the vertex.

        :param _id: Vertex ID.
        :type _id: dict

        :param label: Optional edge label. Defaults to None.
        :type label: str

        :rtype: Response

        """
        raise NotImplementedError 

    def inV(self, _id, label=None):
        """
        Returns the in-adjacent vertices of the vertex.

        :param _id: Vertex ID.
        :type _id: dict

        :param label: Optional edge label. Defaults to None.
        :type label: str

        :rtype: Response

        """
        raise NotImplementedError 

    def bothV(self, _id, label=None):
        """
        Returns the incoming- and outgoing-adjacent vertices of the vertex.

        :param _id: Vertex ID.
        :type _id: dict

        :param label: Optional edge label. Defaults to None.
        :type label: str

        :rtype: Response

        """
        raise NotImplementedError 

    # Index Proxy - Vertex

    def create_vertex_index(self, params):
        """
        Creates a vertex index with the specified params.

        :param index_name: Name of the index to create.
        :type index_name: str

        :rtype: Response

        """
        raise NotImplementedError 

    def get_vertex_index(self, index_name):
        """
        Returns the vertex index with the index_name.

        :param index_name: Name of the index.
        :type index_name: str

        :rtype: Response

        """
        raise NotImplementedError 
        
    def delete_vertex_index(self, index_name): 
        """
        Deletes the vertex index with the index_name.

        :param index_name: Name of the index.
        :type index_name: str

        :rtype: Response

        """
        raise NotImplementedError 

    # Index Proxy - Edge

    def create_edge_index(self, index_name):
        """
        Creates a edge index with the specified params.

        :param index_name: Name of the index.
        :type index_name: str

        :rtype: Response

        """
        raise NotImplementedError 

    def get_edge_index(self, index_name):
        """
        Returns the edge index with the index_name.

        :param index_name: Name of the index.
        :type index_name: str

        :rtype: Response

        """
        raise NotImplementedError 
        
    def delete_edge_index(self, index_name): 
        """
        Deletes the edge index with the index_name.

        :param index_name: Name of the index.
        :type index_name: str

        :rtype: Response

        """
        raise NotImplementedError 
    
    # Index Container - Vertex

    def put_vertex(self, index_name, key, value, _id):
        """
        Adds a vertex to the index with the index_name.

        :param index_name: Name of the index.
        :type index_name: str

        :param key: Name of the key.
        :type key: str

        :param value: Value of the key.
        :type value: str

        :param _id: Vertex ID
        :type _id: int
        
        :rtype: Response

        """
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

        :rtype: Response

        """
        raise NotImplementedError 

    def remove_vertex(self, index_name, _id, key=None, value=None):
        """
        Removes a vertex from the index and returns the Response.

        :param index_name: Name of the index.
        :type index_name: str

        :param key: Optional. Name of the key.
        :type key: str

        :param value: Optional. Value of the key.
        :type value: str        

        :rtype: Response

        """
        raise NotImplementedError 

    # Index Container - Edge

    def put_edge(self, index_name, key, value, _id):
        """
        Adds an edge to the index and returns the Response.

        :param index_name: Name of the index.
        :type index_name: str

        :param key: Name of the key.
        :type key: str

        :param value: Value of the key.
        :type value: str

        :param _id: Edge ID
        :type _id: int
        
        :rtype: Response

        """
        raise NotImplementedError 

    def lookup_edge(self, index_name, key, value):
        """
        Looks up an edge in the index and returns the Response.

        :param index_name: Name of the index.
        :type index_name: str

        :param key: Name of the key.
        :type key: str

        :param value: Value of the key.
        :type value: str

        :rtype: Response

        """
        raise NotImplementedError 

    def remove_edge(self, index_name, _id, key=None, value=None):
        """
        Removes an edge from the index and returns the Response.
        
        :param index_name: Name of the index.
        :type index_name: str

        :param _id: Edge ID
        :type _id: int

        :param key: Optional. Name of the key.
        :type key: str

        :param value: Optional. Value of the key.
        :type value: str        

        :rtype: Response

        """
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

        :rtype: Response

        """
        raise NotImplementedError 

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

        :rtype: Response

        """
        raise NotImplementedError 

    # Model Proxy - Edge

    def create_indexed_edge(self, data, index_name, keys=None):
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

        :rtype: Response

        """
        raise NotImplementedError 

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

        :rtype: Response

        """
        raise NotImplementedError 
    
        
