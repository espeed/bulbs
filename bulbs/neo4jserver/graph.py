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
from bulbs.factory import Factory
from bulbs.graph import Graph as BaseGraph

# Neo4j-specific imports
from resource import Neo4jResource, NEO4J_URI
from index import ExactIndex, UniqueIndex, FulltextIndex

class Graph(BaseGraph):
    """
    The primary interface to graph databases on Neo4j Server.

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
    default_uri = NEO4J_URI
    default_index = ExactIndex
    resource_class = Neo4jResource

    # What happens if these REST calls error on Heroku?

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
        
