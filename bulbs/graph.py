# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Interface for interacting with a graph database through Rexster.

"""

from element import Vertex, VertexProxy, EdgeProxy, Edge
from index import IndexProxy
from gremlin import Gremlin

from config import Config, REXSTER_URI, NEO4J_URI, SAIL_URI
from rexster import RexsterResource, RexsterIndex
from neo4jserver import Neo4jResource, Neo4jIndex

class Graph(object):
    """
    The primary interface to graph databases on the Rexster REST server.

    Instantiates the database :class:`~bulbs.rest.Resource` object using 
    the specified database URL and sets up proxy objects to the database.
    


    :keyword db_url: The URL to the specific database on Rexster. 
    :ivar vertices: :class:`~bulbs.element.VertexProxy` object for the Resource.
    :ivar edges: :class:`~bulbs.element.EdgeProxy` object for the Resource.
    :ivar indices: :class:`~bulbs.index.IndexProxy` object for the Resource.
    :ivar gremlin: :class:`~bulbs.gremlin.Gremlin` object for the Resource.

    Example::

    >>> from bulbs.graph import Graph
    >>> g = Graph()
    >>> james = g.vertices.create({'name':'James'})
    >>> julie = g.vertices.create({'name':'Julie'})
    >>> g.edges.create(james,"knows",julie)

    """

    def __init__(self,resource):
        self.resource = resource
        

    def load_graphml(self,url):
        """
        Loads a GraphML file into the database, and returns the Rexster 
        response object.

        :param url: The URL of the GraphML file to load.

        """
        script = "g.loadGraphML('%s')" % url
        resp = self.gremlin.execute(script)
        return resp

    def save_graphml(self):
        """
        Returns a GraphML file representing the entire database.

        """

        script = """
        g.saveGraphML('data/graphml');
        new File('data/graphml').getText();
        """
        results = self.gremlin.execute(script)
        return results[0]

    def clear(self):
        """
        Deletes all the elements in the graph.

        Example::

        >>> g = Graph()
        >>> g.clear()

        .. admonition:: WARNING 

           g.clear() will delete all your data!

        """
        resp = self.resource.clear()
        return resp




class Neo4jGraph(Graph):
    
    def __init__(self,root_uri=NEO4J_URI):
        config = Config(root_uri)
        resource = Neo4jResource(config)
        Graph.__init__(self,resource)
        
        # Set Indices
        index_proxy = IndexProxy(resource,Neo4jIndex)

        
class RexsterGraph(Graph):

    def __init__(self,root_uri=REXSTER_URI):
        config = Config(root_uri)
        resource = RexsterResource(config)
        Graph.__init__(self,resource)
        self.initialize(resource)
        
    def initialize(self,resource):
        self.gremlin = Gremlin(self.resource)
        self.indices = IndexProxy(RexsterIndex,resource)
        
        self.vertices = VertexProxy(Vertex,resource) 
        self.vertices.index = self.indices.get("vertices") 

        self.edges = EdgeProxy(Edge,resource)
        self.edges.index = self.indices.get("edges")


class SailGraph(object):
    """ An interface to for SailGraph. """

    def __init__(self,root_uri=SAIL_URI):
        config = Config(root_uri)
        self.resource = RexsterResource(config)

        self.vertices = self.create_proxy(Vertex,RexsterIndex,"vertices") 
        self.edges = self.create_proxy(Edge,RexsterIndex,"edges")
        self.gremlin = Gremlin(self.resource)

        
    def add_prefix(self,prefix,namespace):
        params = dict(prefix=prefix,namespace=namespace)
        resp = self.resource.post(self._base_target(),params)
        return resp

    def get_all_prefixes(self):
        resp = self.resource.get(self._base_target(),params=None)
        return resp.results

    def get_prefix(self,prefix):
        target = "%s/%s" % (self._base_target(), prefix)
        resp = self.resource.get(target,params=None)
        return resp.results
        
    def remove_prefix(self,prefix):
        target = "%s/%s" % (self._base_target(), prefix)
        resp = self.resource.delete(target,params=None)
        return resp

    def load_rdf(self,url):
        """
        Loads an RDF file into the database, and returns the Rexster 
        response object.

        :param url: The URL of the RDF file to load.

        """
        script = "g.loadRDF('%s', 'n-triples')" % url
        params = dict(script=script)
        resp = self.resource.get(self.base_target,params)
        return resp

    def _base_target(self):
        "Returns the base target URL path for vertices on Rexster."""
        base_target = "%s/%s" % (self.resource.db_name,"prefixes")
        return base_target
