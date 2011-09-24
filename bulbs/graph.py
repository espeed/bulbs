# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Interface for interacting with a graph database through Rexster.

"""
import config
from rest import Resource
from element import Vertex, VertexProxy, Edge, EdgeProxy
from index import IndexProxy
from gremlin import Gremlin

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

    def __init__(self,db_url=config.DATABASE_URL):
        self.resource = Resource(db_url)
        self.vertices = VertexProxy(self.resource)
        self.edges = EdgeProxy(self.resource)
        self.indices = IndexProxy(self.resource)
        self.gremlin = Gremlin(self.resource)

    #def __rshift__(self,b):
    #    return list(self)

    @property
    def V(self):
        """
        Returns all the vertices of the graph.

        Example::
        
        >>> g = Graph()
        >>> vertices = g.V

        :rtype: List of :class:`~bulbs.element.Vertex` objects. 

        """
        vertices = self.gremlin.query("g.V",Vertex,raw=True)
        return list(vertices)
    
    @property
    def E(self):
        """
        Returns all the edges of the graph. 

        Example::
        
        >>> g = Graph()
        >>> edges = g.E

        :rtype: List of :class:`~bulbs.element.Edge` objects.

        """
        edges = self.gremlin.query("g.E",Edge,raw=True)
        return list(edges)

    def idxV(self,**kwds):
        """
        Looks up a key/value pair in the vertex index and
        returns a generator containing the vertices matching the key and value.

        :keyword pair: The key/value pair to match on.
        :keyword raw: Boolean. If True, return the raw Response object. 
                      Defaults to False.

        Example::

        >>> g = Graph()
        >>> vertices = g.idxV(name="James")

        :rtype: Generator of :class:`~bulbs.element.Vertex` objects.

        You can turn the generator into a list by doing::

        >>> vertices = g.idxV(name="James")
        >>> vertices = list(vertices)

        """
        return self._idx("vertices",**kwds)
        
    #def _initialize_results(self,results,raw):
    #    if raw is True:
    #        return (result for result in results)
    #    else:
    #        return (Vertex(self.resource,result) for result in results)
        
    def idxE(self,**kwds):
        """
        Looks up a key/value pair in the edge index and 
        returns a generator containing the edges matching the key and value.

        :keyword pair: The key/value pair to match on.
        :keyword raw: Boolean. If True, return the raw Response object. 
                      Defaults to False.

        Example::

        >>> g = Graph()
        >>> edges = g.idxE(label="knows")

        :rtype: Generator of :class:`~bulbs.element.Edge` objects.

        You can turn the generator into a list by doing::

        >>> edges = g.idxE(label="knows")
        >>> edges = list(edges)

        """
        return self._idx("edges",**kwds)

    def _idx(self,index_name,**kwds):
        """
        Returns the Rexster Response object of the index look up.
        
        :param index_name: The name of the index.

        :param pair: The key/value pair to match on. 
        :keyword raw: Boolean. If True, return the raw Response object. 
                      Defaults to False.

        """
        raw = kwds.pop("raw",False)
        key, value = kwds.popitem()
        target = "%s/indices/%s" % (self.resource.db_name,index_name)
        params = dict(key=key,value=value)
        resp = self.resource.get(target,params)
        if raw:
            return resp
        if resp.results:
            class_map = dict(vertices=Vertex,edges=Edge)
            element_class = class_map[index_name]
            return (element_class(self.resource,result) for result in resp.results)

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
        target = self.resource.db_name
        resp = self.resource.delete(target,params=None)
        return resp


class SailGraph(Graph):
    """ An interface to for SailGraph. """

    def __init__(self,db_url=config.SAIL_URL):
        Graph.__init__(self,db_url)
        
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

