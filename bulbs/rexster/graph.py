# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Interface for interacting with a graph database through Neo4j Server.

"""
from bulbs.gremlin import Gremlin
from bulbs.element import Vertex, VertexProxy, Edge, EdgeProxy

# Rexster-specific imports
from .client import Neo4jClient, NEO4J_URI
from .index import ManualIndex, IndexProxy

class Graph(object):

    def __init__(self,root_uri=REXSTER_URI):
        self.config = Config(root_uri)
        self.client = RexsterClient(self.config)

        self.gremlin = Gremlin(self.client)
        self.indices = IndexProxy(RexsterIndex,client)

        self.vertices = VertexProxy(Vertex,self.client)
        self.vertices.index = self.indices.get("vertices",Vertex)
 
        self.edges = EdgeProxy(Edge,self.client)
        self.edges.index = self.indices.get("edges",Edge)

    def load_graphml(self,uri):
        """Loads a GraphML file into the database and returns the response."""
        script = self.client.scripts.get('load_graphml')
        params = dict(uri=uri)
        return self.gremlin.execute(script,params)
        
    def save_graphml(self):
        """Returns a GraphML file representing the entire database."""
        script = self.client.scripts.get('save_graphml')
        results = self.gremlin.execute(script,params=None)
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
        return self.client.clear()


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
