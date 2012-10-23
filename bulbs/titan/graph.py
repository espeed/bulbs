# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Interface for interacting with a graph database through Rexster.

"""
from bulbs.config import Config
from bulbs.gremlin import Gremlin
from bulbs.element import Vertex, Edge
from bulbs.model import Node, Relationship
from bulbs.base.graph import Graph as BaseGraph

# Rexster-specific imports
from .client import TitanClient
from .index import KeyIndex


class Graph(BaseGraph):
    """
    The primary interface to Rexster.

    Instantiates the database :class:`~bulbs.rexster.client.Client` object using 
    the specified Config and sets up proxy objects to the database.

    :param config: Optional. Defaults to the default config.
    :type config: bulbs.config.Config

    :cvar client_class: RexsterClient class.
    :cvar default_index: Default index class.

    :ivar client: RexsterClient object.
    :ivar vertices: VertexProxy object.
    :ivar edges: EdgeProxy object.
    :ivar config: Config object.
    :ivar gremlin: Gremlin object.
    :ivar scripts: GroovyScripts object.
    
    Example:

    >>> from bulbs.rexster import Graph
    >>> g = Graph()
    >>> james = g.vertices.create(name="James")
    >>> julie = g.vertices.create(name="Julie")
    >>> g.edges.create(james, "knows", julie)

    """
    client_class = TitanClient
    default_index = KeyIndex
    
    def __init__(self, config=None):
        super(Graph, self).__init__(config)

        # Rexster supports Gremlin
        self.gremlin = Gremlin(self.client)
        self.scripts = self.client.scripts    # for convienience 


    def load_graphml(self,uri):
        """
        Loads a GraphML file into the database and returns the response.

        :param uri: URI of the GraphML file to load.
        :type uri: str

        :rtype: RexsterResult

        """
        script = self.client.scripts.get('load_graphml')
        params = dict(uri=uri)
        return self.gremlin.command(script, params)
        
    def get_graphml(self):
        """
        Returns a GraphML file representing the entire database.

        :rtype: RexsterResult

        """
        script = self.client.scripts.get('save_graphml')
        return self.gremlin.command(script, params=None)
        
    def warm_cache(self):
        """
        Warms the server cache by loading elements into memory.

        :rtype: RexsterResult

        """
        script = self.scripts.get('warm_cache')
        return self.gremlin.command(script, params=None)

    def clear(self):
        """
        Deletes all the elements in the graph.

        :rtype: RexsterResult

        .. admonition:: WARNING 

           This will delete all your data!

        """
        script = self.client.scripts.get('clear')
        return self.gremlin.command(script,params=None)


