
class Sugar(object):
    """Graph mixin containing some syntactic sugar."""

    def __init__(self,client):
        self.client = client


    @property
    def V(self):
        """
        Returns all the vertices of the graph.

        Example::
        
        >>> g = Graph()
        >>> vertices = g.V

        :rtype: List of :class:`~bulbs.element.Vertex` objects. 

        """
        resp = self.client.gremlin("g.V")
        return list(resp.results)
    
    @property
    def E(self):
        """
        Returns all the edges of the graph. 

        Example::
        
        >>> g = Graph()
        >>> edges = g.E

        :rtype: List of :class:`~bulbs.element.Edge` objects.

        """
        resp = self.client.gremlin("g.E")
        return list(resp.results)

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
        index_name = "vertices"
        key, value = kwds.popitem()
        resp = self.client.lookup_vertex(index_name,key,value)
        if resp.results:
            return (Vertex(self.client,result) for result in resp.results)
        
        
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
        index_name = "edges"
        key, value = kwds.popitem()
        resp = self.client.lookup_edge(index_name,key,value)
        if resp.results:
            return (Edge(self.client,result) for result in resp.results)

