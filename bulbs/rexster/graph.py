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
from .client import RexsterClient, SAIL_URI
from .index import ManualIndex


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
    client_class = RexsterClient
    default_index = ManualIndex
    
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


#
# SailGraph is Undocumented/Experimental - Not Current
#

# TODO: Create a SailClient or sail Client methods.

class SailGraph(object):
    """ An interface to for SailGraph. """

    def __init__(self,root_uri=SAIL_URI):
        self.config = Config(root_uri)
        self.client = RexsterClient(self.config)

        # No indices on sail graphs
        self.gremlin = Gremlin(self.client)        

        self.vertices = VertexProxy(Vertex,self.client)
        self.edges = EdgeProxy(Edge,self.client)

    def add_prefix(self,prefix,namespace):
        params = dict(prefix=prefix,namespace=namespace)
        resp = self.client.post(self._base_target(),params)
        return resp

    def get_all_prefixes(self):
        resp = self.client.get(self._base_target(),params=None)
        return resp.results

    def get_prefix(self,prefix):
        target = "%s/%s" % (self._base_target(), prefix)
        resp = self.client.get(target,params=None)
        return resp.results
        
    def remove_prefix(self,prefix):
        target = "%s/%s" % (self._base_target(), prefix)
        resp = self.client.delete(target,params=None)
        return resp

    def load_rdf(self,url):
        """
        Loads an RDF file into the database, and returns the Rexster 
        response object.

        :param url: The URL of the RDF file to load.

        """
        script = "g.loadRDF('%s', 'n-triples')" % url
        params = dict(script=script)
        resp = self.client.get(self.base_target,params)
        return resp

    def _base_target(self):
        "Returns the base target URL path for vertices on Rexster."""
        base_target = "%s/%s" % (self.client.db_name,"prefixes")
        return base_target
