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
from bulbs.element import Vertex, VertexProxy, Edge, EdgeProxy

# Neo4j-specific imports
from resource import Neo4jResource, NEO4J_URI
from index import ExactIndex, VertexIndexProxy, EdgeIndexProxy

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

        self.gremlin = Gremlin(self.resource)

        self.indicesV = VertexIndexProxy(ExactIndex,self.resource)
        self.indicesE = EdgeIndexProxy(ExactIndex,self.resource)
        
        # What happens if these REST calls error on Heroku?

        self.vertices = VertexProxy(Vertex,self.resource)
        self.vertices.index = self.indicesV.get_or_create("vertices")
 
        self.edges = EdgeProxy(Edge,self.resource)
        self.edges.index = self.indicesE.get_or_create("edges")

    def load_graphml(self,uri):
        """Loads a GraphML file into the database and returns the response."""
        script = self.resource.scripts.get('load_graphml')
        params = dict(uri=uri)
        return self.gremlin.execute(script,params)
        
    def save_graphml(self):
        """Returns a GraphML file representing the entire database."""
        script = self.resource.scripts.get('save_graphml')
        results = self.gremlin.execute(script,params=None)
        return results[0]

    def clear(self):
        """Deletes all the elements in the graph.

        .. admonition:: WARNING 

           g.clear() will delete all your data!

        """
        return self.resource.clear()
        
