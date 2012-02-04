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
from bulbs.proxy import ProxyFactory

# Neo4j-specific imports
from resource import Neo4jResource, NEO4J_URI
from index import INDEX_PROXIES, ExactIndex, UniqueIndex, FulltextIndex

class Graph(object):
    """
    The primary interface to graph databases on the Rexster REST server.

    Instantiates the database :class:`~bulbs.rest.Resource` object using 
    the specified database URL and sets up proxy objects to the database.

    :keyword root_uri: The URI to Neo4j Server. 
    
    Example::

    >>> from bulbs.neo4jserver import Graph
    >>> g = Graph()
    >>> james = g.vertices.create({'name':'James'})
    >>> julie = g.vertices.create({'name':'Julie'})
    >>> g.edges.create(james,"knows",julie)
    >>> g.vertices.index.lookup(name="James")

    """

    
    def __init__(self,root_uri=NEO4J_URI):
        self.config = Config(root_uri)
        self.resource = Neo4jResource(self.config)
        self.proxies = ProxyFactory(self.resource, ELEMENT_PROXIES, INDEX_PROXIES)
        self.default_index_class = ExactIndex

        self.gremlin = Gremlin(self.resource)

        # What happens if these REST calls error on Heroku?
        self.vertices = self.build_proxy(Vertex, ExactIndex)
        self.edges = self.build_proxy(Edge, ExactIndex)

        self.relationships = self.build_proxy(Relationship, ExactIndex)

    def add_proxy(self, proxy_name, element_class, index_class=None):
        """Adds an element proxy to an existing Graph object."""
        proxy = self.build_proxy(element_class, index_class)
        setattr(self, proxy_name, proxy)
    
    def build_proxy(self, element_class, index_class=None):
        """Returns an element proxy built to specifications."""
        if not index_class:
            index_class = self.default_index_class
        return self.proxies.build_element_proxy(element_class, index_class)

    def load_graphml(self,uri):
        """Loads a GraphML file into the database and returns the response."""
        script = self.resource.scripts.get('load_graphml')
        params = dict(uri=uri)
        return self.gremlin.command(script,params)
        
    def save_graphml(self):
        """Returns a GraphML file representing the entire database."""
        script = self.resource.scripts.get('save_graphml')
        return self.gremlin.command(script,params=None)
        
    def clear(self):
        """Deletes all the elements in the graph.

        .. admonition:: WARNING 

           This will delete all your data!

        """
        script = self.resource.scripts.get('clear')
        return self.gremlin.command(script,params=None)
        
