# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Vertex and Edge container classes and associated proxy classes.

"""


from .utils import initialize_element, initialize_elements, coerce_id
from .utils import u  # Python 3 unicode

class Element(object):
    """
    An abstract base class for Vertex and Edge containers.

    """
    def __init__(self, client):

        #: Client object....
        self._client = client

        #: Property data
        self._data = {}

    def _initialize(self, result):
        """
        Initialize the element after its data has been returned by the database.

        :param result: The Result object returned by the the Client request.
        :param result: Result

        

        """
        # initialize all non-database properties here because
        # __setattr__ will assume all non-defined properties are database properties
        self._result = result
        self._data = result.get_map().copy() # Do we really need/want to make a copy?
        self._set_pretty_id(self._client)
        # These vertex and edge proxies are only used for gets, not mutable stuff
        self._vertices = VertexProxy(Vertex,self._client)
        self._edges = EdgeProxy(Edge,self._client)
        self._initialized = True
       
    @classmethod
    def get_base_type(cls):
        raise NotImplementedError 

    @classmethod
    def get_element_key(cls, config):
        raise NotImplementedError 

    @classmethod
    def get_index_name(cls, config):
        raise NotImplementedError 

    @classmethod
    def get_proxy_class(cls):
        raise NotImplementedError 

    @property
    def _id(self):
        """
        Returns the element ID. This is the element's "primary key"; however,
        some DBs (such as neo4j) reuse IDs if they are deleted so be careful 
        with how you use them. If you want to guarantee they are unique across 
        the DB's lifetime either don't physically delete elements and just set 
        a deleted flag, or use some other mechanism, such as an external 
        sequence or a hash.

        :rtype: int or str

        """
        return self._result.get_id()

    @property 
    def _type(self):
        """
        Returns the element's base type, either vertex or edge.

        :rtype: str

        """
        return self._result.get_type()

    def _set_pretty_id(self, client):
        """
        Sets the ID var specified in Config as a Python property. Defaults to eid.
        
        The user-configured element_type and label vars are not set because 
        they are class vars so you set those when you create the Model.

        """
        pretty_var = client.config.id_var
        fget = lambda self: self._result.get_id()
        setattr(Element,pretty_var,property(fget))                    

    def __setattr__(self, key, value):
        """
        Overloaded to set the object attributes or the property data.

        If you explicitly set/change the values of an element's properties,
        make sure you call save() to updated the values in the DB.

        :rtype: None

        """
        _initialized = getattr(self,"_initialized",False)
        if key in self.__dict__ or _initialized is False:
            # set the attribute normally
            object.__setattr__(self, key, value)
        else:
            # set the attribute as a data property
            self._data[key] = value

    def __getattr__(self,name):
        """
        Returns the value of the database property for the given name.

        :param name: The name of the data property.
        :type name: str

        :raises: AttributeError

        :rtype: str, int, long, float, list, dict, or None 
        
        """
        try:
            return self._data[name]
        except:
            raise AttributeError(name)

    def __len__(self):
        """Returns the number of items stored in the DB results"""
        return len(self._data)

    def __contains__(self, item):
        """Returns True if attribute is a key that has been stored in the DB"""
        return item in self._data

    def __eq__(self, obj):
        """Returns True if the elements are equal"""
        return (hasattr(obj, "__class__") and
                self.__class__ == obj.__class__ and
                self._id == obj._id and
                self._data == obj._data)

    def __ne__(self, obj):
        """Returns True if the elements are not equal."""
        return not self.__eq__(obj)

    def __repr__(self):
        """Returns the string representation of the attribute."""
        return self.__unicode__()
    
    def __str__(self):
        """Returns the string representation of the attribute."""
        return self.__unicode__()
    
    def __unicode__(self):
        """Returns the unicode representation of the attribute."""
        return u("<%s: %s>" % (self.__class__.__name__,self._result.get_uri()))  # Python 3

    def get(self, name):
        return getattr(self, name, None)

    def map(self):
        """
        Returns the element's property data.

        :rtype: dict

        """
        return self._data


#
# Vertices
#

class Vertex(Element):
    """
    A container for a Vertex returned by a client proxy.

    :param client: The Client object for the database.
    :type client: Client

    Example:
        
    >>> from bulbs.neo4jserver import Graph
    >>> g = Graph()
    # Get a vertex from the database.
    >>> james = g.vertices.get(3)
    >>> james.age = 34
    >>> james.save()
    >>> james.map()
    {'age': 34, 'name': 'James'}
    >>> friends = james.outV("knows")

    """  
    @classmethod
    def get_base_type(cls):
        """
        Returns the base type, which is "vertex". Don't override this.
        
        :rtype: str
        
        """
        #: Don't override this
        return "vertex"

    @classmethod
    def get_element_key(cls, config):
        """
        Returns the element key. Defaults to "vertex". Override this in Model.

        :rtype: str

        """
        return "vertex"

    @classmethod 
    def get_index_name(cls, config):
        """
        Returns the index name. Defaults to the value of Config.vertex_index. 

        :rtype: str

        """
        return config.vertex_index

    @classmethod 
    def get_proxy_class(cls):
        """
        Returns the proxy class. Defaults to VertexProxy.

        :rtype: class

        """
        return VertexProxy

    def outE(self,label=None):
        """
        Returns the outgoing edges of the vertex.

        :param label: An optional edge label.
        :type label: str or None

        :rtype: Edge generator

        """
        resp = self._client.outE(self._id,label)
        return initialize_elements(self._client,resp)

    def inE(self,label=None):
        """
        Returns the incoming edges of the vertex.

        :param label: An optional edge label.
        :type label: str or None

        :rtype: Edge generator

        """
        resp = self._client.inE(self._id,label)
        return initialize_elements(self._client,resp)

    def bothE(self,label=None):
        """
        Returns the incoming and outgoing edges of the vertex.

        :param label: An optional edge label.
        :type label: str or None

        :rtype: Edge generator

        """
        resp = self._client.bothE(self._id,label)
        return initialize_elements(self._client,resp)

    def outV(self,label=None):
        """
        Returns the out-adjacent vertices of the vertex.

        :param label: An optional edge label.
        :type label: str or None

        :rtype: Vertex generator

        """
        resp = self._client.outV(self._id,label)
        return initialize_elements(self._client,resp)

    def inV(self,label=None):
        """
        Returns the in-adjacent vertices of the vertex.

        :param label: An optional edge label.
        :type label: str or None

        :rtype: Vertex generator

        """
        resp = self._client.inV(self._id,label)
        return initialize_elements(self._client,resp)
        
    def bothV(self,label=None):
        """
        Returns all incoming- and outgoing-adjacent vertices of vertex.

        :param label: An optional edge label.
        :type label: str or None

        :rtype: Vertex generator

        """
        resp = self._client.bothV(self._id,label)
        return initialize_elements(self._client,resp)

    def save(self):
        """
        Saves the vertex on the client.

        :rtype: Response

        """
        return self._vertices.update(self._id, self._data)
    

    #def _create(self,_data=None,**kwds):
    #    data = build_data(_data, kwds)
    #    resp = self.client.create_vertex(data)
    #    self._initialize(resp.results)
        
    #def _update(self,_id, _data=None, **kwds):
    #    data = build_data(_data, kwds)
    #    resp = self.client.update_vertex(_id,_data)
    #    # with Neo4j, there is nothting to initialize
    #    self._initialize(resp.results)
        
        

class VertexProxy(object):
    """ 
    A proxy for interacting with vertices on the Client. 

    :param element_class: The element class to be managed by this proxy instance.
    :type element_class: Vertex or Edge class

    :param client: The Client object for the database.
    :type client: Client

    Example::
        
    >>> from bulbs.neo4jserver import Graph
    >>> g = Graph()
    >>> james = g.vertices.create({'name':'James'})
    >>> data = dict(name="James", age=34)
    >>> g.vertices.update(james.eid, data)
    >>> james = g.vertices.get(james.eid)
    >>> g.vertices.remove_properties(james.eid)
    >>> g.vertices.delete(james.eid)

    """

    def __init__(self,element_class,client):
        assert issubclass(element_class,Vertex)
        self.element_class = element_class
        self.client = client
        self.client.registry.add_class(element_class)
        self.index = None

    def create(self, _data=None, **kwds):
        """
        Adds a vertex to the database and returns it.

        :param data: A dict containing the vettex's property data.
        :type data: dict

        :rtype: Vertex

        """
        data = build_data(_data, kwds)
        resp = self.client.create_vertex(data)
        return initialize_element(self.client,resp.results)

    def get(self, _id):
        """
        Returns the vertex for the given ID.

        :param _id: The vertex ID.
        :type _id: int or str

        :rtype: Vertex

        """
        try:
            resp = self.client.get_vertex(_id)
            return initialize_element(self.client,resp.results)
        except LookupError:
            return None
        
    def get_or_create(self, key, value, _data=None, **kwds):
        # TODO: This will only index for non-models if autoindex is True.
        # Relationship Models are set to index by default, but 
        # EdgeProxy doesn't have this method anyway.
        vertex = self.index.get_unique(key, value)
        if vertex is None:
            vertex = self.create(_data, **kwds)
        return vertex

    # is this really needed?
    def get_all(self):
        """
        Returns all the vertices in the graph.
        
        :rtype: Vertex generator
 
        """
        resp = self.client.get_all_vertices()
        return initialize_elements(self.client, resp)

    def update(self,_id, _data=None, **kwds):
        """
        Updates an element in the graph DB and returns it.

        :param _id: The vertex ID.
        :type _id: int or str

        :rtype: Response

        """ 
        # NOTE: this no longer returns an initialized element because not all 
        # Clients return element data, e.g. Neo4jServer retuns nothing.
        data = build_data(_data, kwds)
        self.client.update_vertex(_id,_data)

    # is this really needed?    
    def remove_properties(self,_id):
        """
        Removes all properties from a vertex and returns the response.

        :param _id: The vertex ID.
        :type _id: int or str

        :rtype: Response

        """ 
        return self.client.remove_vertex_properties(_id)
                    
    def delete(self,_id):
        """
        Deletes a vertex from a graph DB and returns the response.

        :param _id: The vertex ID.
        :type _id: int or str

        :rtype: Response
        
        """
        return self.client.delete_vertex(_id)


#
# Edges
#

class Edge(Element):
    """
    A container for an Edge returned by a client proxy.

    :param client: The Client object for the database.
    :type client: Client

    Example:
        
    >>> from bulbs.neo4jserver import Graph
    >>> g = Graph()
    # Get an edge from the database
    >>> edge = g.edges.get(8)
    >>> edge.label()
    'knows'
    >>> edge.outV()
    <Vertex: http://localhost:7474/db/data/node/5629>
    >>> edge._outV
    5629
    >>> edge.inV()
    <Vertex: http://localhost:7474/db/data/node/5630>
    >>> edge._inV
    5630
    >>> edge.weight = 0.5
    >>> edge.save()
    >>> edge.map()
    {'weight': 0.5}

    """

    @classmethod
    def get_base_type(cls):
        """
        Returns the base type, which is "edge". Don't override this.
        
        :rtype: str
        
        """
        #: Don't override this
        return "edge"

    @classmethod
    def get_element_key(cls, config):
        """
        Returns the element key. Defaults to "edge". Override this in Model.

        :rtype: str

        """
        return "edge"

    @classmethod 
    def get_index_name(cls, config):
        """
        Returns the index name. Defaults to the value of Config.edge_index. 

        :rtype: str

        """
        return config.edge_index

    @classmethod 
    def get_proxy_class(cls):
        """
        Returns the proxy class. Defaults to EdgeProxy.

        :rtype: class

        """
        return EdgeProxy

    @property
    def _outV(self):
        """
        Returns the outgoing vertex ID of the edge.

        :rtype: int

        """
        return self._result.get_outV()
        
    @property
    def _inV(self):
        """
        Returns the incoming vertex ID of the edge.

        :rtype: int

        """
        return self._result.get_inV()
        
    @property
    def _label(self):
        """
        Returns the edge's label.

        :rtype: str

        """
        return self._result.get_label()
        
    def outV(self):
        """
        Returns the outgoing Vertex of the edge.

        :rtype: Vertex

        """
        return self._vertices.get(self._outV)
    
    def inV(self):
        """
        Returns the incoming Vertex of the edge.

        :rtype: Vertex

        """
        return self._vertices.get(self._inV)

    def label(self):
        """
        Returns the edge's label.

        :rtype: str

        """
        return self._result.get_label()

    def save(self):
        """
        Saves the edge on the client.

        :rtype: Response

        """
        return self._edges.update(self._id, self._data)


    
class EdgeProxy(object):
    """ 
    A proxy for interacting with edges on the Client. 

    Example::
        
    >>> from bulbs.neo4jserver import Graph
    >>> g = Graph()
    >>> james = g.vertices.create({'name':'James'})
    >>> julie = g.vertices.create({'name':'Julie'})
    >>> knows = g.edges.create(james,"knows",julie)
    >>> knows = g.edges.get(knows.eid)
    >>> data = dict(weight=0.5)
    >>> g.edges.update(knows.eid, data)
    >>> g.edges.remove_properties(knows.eid)
    >>> g.edges.delete(knows.eid)

    """

    def __init__(self,element_class,client):
        assert issubclass(element_class,Edge)
        self.element_class = element_class
        self.client = client
        self.client.registry.add_class(element_class)
        self.index = None

    def create(self,outV,label,inV,_data=None,**kwds):
        """
        Creates an edge in the database and returns it.
        
        :param outV: The outgoing vertex. 
        :type outV: Vertex or int
                      
        :param label: The edge's label.
        :type label: str

        :param inV: The incoming vertex. 
        :type inV: Vertex or int

        :param data: The edge's property data.
        :type data: dict

        :rtype: Edge

        """ 
        assert label is not None
        data = build_data(_data, kwds)
        outV, inV = coerce_vertices(outV, inV)
        resp = self.client.create_edge(outV,label,inV,data)
        return initialize_element(self.client,resp.results)

    def get(self,_id):
        """
        Retrieves an edge from the database and returns it.

        :param _id: The edge ID.
        :type _id: int or str

        :rtype: Edge

        """
        try:
            resp = self.client.get_edge(_id)
            return initialize_element(self.client,resp.results)
        except LookupError:
            return None

    # is this really needed?
    def get_all(self):
        """
        Returns all the edges in the graph.
        
        :rtype: Edge generator
 
        """
        resp = self.client.get_all_edges()
        return initialize_elements(self.client, resp)


    def update(self,_id,_data=None,**kwds):
        """ 
        Updates an edge in the database and returns it. 
        
        :param _id: The edge ID.
        :type _id: int or str

        :param data: A dict containing the edge's property data.
        :type data: dict

        :rtype: Response

        """
        # NOTE: this no longer returns an initialized element because 
        # not all Clients return element data, e.g. Neo4jServer retuns nothing.
        data = build_data(_data, kwds)
        return self.client.update_edge(_id, data)
                    
    def remove_properties(self,_id):
        """
        Removes all properties from a element and returns the response.
        
        :param _id: The edge ID.
        :type _id: int or str

        :rtype: Response
        
        """
        return self.client.remove_edge_properties(_id)

    def delete(self,_id):
        """
        Deletes a vertex from a graph DB and returns the response.
        
        :param _id: The edge ID.
        :type _id: int or str

        :rtype: Response

        """
        return self.client.delete_edge(_id)


#
# Element Utils
#

def build_data(_data, kwds):
    # Doing this rather than defaulting the _data arg to {}
    data = {} if _data is None else _data
    data.update(kwds)
    return data

def coerce_vertices(outV, inV):
    outV = coerce_vertex(outV)
    inV = coerce_vertex(inV)
    return outV, inV
  
def coerce_vertex(vertex):
    """
    Coerces an object into a vertex ID and returns it.
    
    :param vertex: The object we want to coerce into a vertex ID.
    :type vertex: Vertex object or vertex ID.

    :rtype: int or str

    """
    if isinstance(vertex, Vertex):
        vertex_id = vertex._id
    else:
        # the vertex ID may have been passed in as a string
        # using corece_id to support OrientDB and linked-data URI (non-integer) IDs
        vertex_id = coerce_id(vertex)
    return vertex_id



