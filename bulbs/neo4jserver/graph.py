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
from client import Neo4jClient, NEO4J_URI
from index import ExactIndex, UniqueIndex, FulltextIndex


class Graph(BaseGraph):
    """
    The primary interface to graph databases on Neo4j Server.

    Instantiates the database :class:`~bulbs.rest.Client` object using 
    the specified database URL and sets up proxy objects to the database.

    :param config: Optional. Defaults to the default config.
    :type config: bulbs.config.Config
    
    Example::

    >>> from bulbs.neo4jserver import Graph
    >>> g = Graph()
    >>> james = g.vertices.create(name="James")
    >>> julie = g.vertices.create(name="Julie")
    >>> g.edges.create(james, "knows", julie)

    """
    #: The default root URI to use for the server Client.
    default_uri = NEO4J_URI

    #: The default Index class.
    default_index = ExactIndex

    #: The Client class to use for this Graph.
    client_class = Neo4jClient

    def __init__(self, config=None):
        # What happens if these REST init calls error on Heroku?    
        super(Graph, self).__init__(config)

        self.gremlin = Gremlin(self.client)

    def load_graphml(self,uri):
        """Loads a GraphML file into the database and returns the response."""
        script = self.client.scripts.get('load_graphml')
        params = dict(uri=uri)
        return self.gremlin.command(script,params)
        
    def save_graphml(self):
        """Returns a GraphML file representing the entire database."""
        script = self.client.scripts.get('save_graphml')
        return self.gremlin.command(script,params=None)
        
    def clear(self):
        """Deletes all the elements in the graph.

        .. admonition:: WARNING 

           This will delete all your data!

        """
        script = self.client.scripts.get('clear')
        return self.gremlin.command(script,params=None)
        
