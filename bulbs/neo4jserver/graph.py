# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Interface for interacting with a graph database through Neo4j Server.

"""
from bulbs.config import Config
from bulbs.gremlin import Gremlin
from bulbs.element import Vertex, Edge
from bulbs.model import Node, Relationship
from bulbs.base.graph import Graph as BaseGraph

# Neo4j-specific imports
from .client import Neo4jClient
from .index import ExactIndex
from .cypher import Cypher

class Graph(BaseGraph):
    """
    The primary interface to Neo4j Server.

    Instantiates the database :class:`~bulbs.neo4jserver.client.Client` object using 
    the specified Config and sets up proxy objects to the database.

    :param config: Optional. Defaults to the default config.
    :type config: bulbs.config.Config

    :cvar client_class: Neo4jClient class.
    :cvar default_index: Default index class.

    :ivar client: Neo4jClient object.
    :ivar vertices: VertexProxy object.
    :ivar edges: EdgeProxy object.
    :ivar config: Config object.
    :ivar gremlin: Gremlin object.
    :ivar scripts: GroovyScripts object.
    
    Example:

    >>> from bulbs.neo4jserver import Graph
    >>> g = Graph()
    >>> james = g.vertices.create(name="James")
    >>> julie = g.vertices.create(name="Julie")
    >>> g.edges.create(james, "knows", julie)

    """
    client_class = Neo4jClient
    default_index = ExactIndex

    def __init__(self, config=None):
        # What happens if these REST init calls error on Heroku?    
        super(Graph, self).__init__(config)

        # Neo4j Server supports Gremlin
        self.gremlin = Gremlin(self.client)
        self.scripts = self.client.scripts    # for convienience 

        # Cypher; TODO: Cypher Queries library object
        self.cypher = Cypher(self.client)

    def set_metadata(self, key, value):
        """
        Sets the metadata key to the supplied value.

        :param key: Metadata key
        :type key: str

        :param value: Metadata value.
        :type value: str, int, or list

        :rtype: Neo4jResponse
        
        """
        return self.client.set_metadata(key, value).one()

    def get_metadata(self, key, default_value=None):
        """
        Returns the value of metadata for the key.

        :param key: Metadata key
        :type key: str

        :param default_value: Default value to return if the key is not found.
        :type default_value: str, int, or list

        :rtype: Neo4jResult
        
        """
        return self.client.get_metadata(key, default_value).one()

    def remove_metadata(self, key):
        """
        Removes the metadata key and value.

        :param key: Metadata key
        :type key: str

        :rtype: Neo4jResponse
        
        """
        return self.client.remove_metadata(key)
        
    def load_graphml(self, uri):
        """
        Loads a GraphML file into the database and returns the response.

        :param uri: URI of the GraphML file to load.
        :type uri: str

        :rtype: Neo4jResult

        """
        script = self.client.scripts.get('load_graphml')
        params = dict(uri=uri)
        return self.gremlin.command(script, params)
        
    def get_graphml(self):
        """
        Returns a GraphML file representing the entire database.

        :rtype: Neo4jResult

        """
        script = self.client.scripts.get('save_graphml')
        return self.gremlin.command(script, params=None)
        
    def warm_cache(self):
        """
        Warms the server cache by loading elements into memory.

        :rtype: Neo4jResult

        """
        script = self.scripts.get('warm_cache')
        return self.gremlin.command(script, params=None)

    def clear(self):
        """
        Deletes all the elements in the graph.

        :rtype: Neo4jResult

        .. admonition:: WARNING 

           This will delete all your data!

        """
        script = self.client.scripts.get('clear')
        return self.gremlin.command(script, params=None)
        
