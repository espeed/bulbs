# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Vertex and Edge container classes and associated proxy classes.

"""
from .utils import u  # Python 3 unicode
from .utils import initialize_element, initialize_elements, coerce_id, get_logger

log = get_logger(__name__)


class Element(object):
    """An abstract base class for Vertex and Edge containers."""

    def __init__(self, client):

        # NOTE: moved all private prop defs here so they are declared and
        # pre-defined in _properties so that setattr works in model NORMAL mode

        # Client object
        self._client = client

        # Property data
        self._data = {}

        # Result object.
        self._result = None

        # Vertex Proxy Object
        self._vertices = None

        # Edge Proxy Object
        self._edges = None

        # Initialized Flag
        # Initialize all non-database properties here because when _initialized
        # is set to True, __setattr__ will assume all non-defined properties 
        # are database properties and will set them in self._data.
        self._initialized = True

    def _initialize(self, result):
        """
        Initialize the element with the result that was returned by the DB.

        :param result: The Result object returned by the the Client request.
        :type result: Result

        :rtype: None

        """
        self._result = result

        # TODO: Do we really need to make a copy?
        self._data = result.get_data().copy() 

        # Sets the element ID to the var defined in Config. Defaults to eid.
        self._set_pretty_id(self._client)

        # These vertex and edge proxies are primarily used for gets; 
        # all mutable methods that use these are overloaded in Model.
        self._vertices = VertexProxy(Vertex,self._client)
        self._edges = EdgeProxy(Edge,self._client)

       
    @classmethod
    def get_base_type(cls):
        """
        Returns this element class's base type.
        
        :rtype: str
        
        """
        raise NotImplementedError 

    @classmethod
    def get_element_key(cls, config):
        """
        Returns the element key.

        :param config: Config object.
        :type config: bulbs.config.Config

        :rtype: str

        """
        raise NotImplementedError 

    @classmethod
    def get_index_name(cls, config):
        """
        Returns the index name. 

        :param config: Config object.
        :type config: bulbs.config.Config

        :rtype: str

        """
        raise NotImplementedError 

    @classmethod
    def get_proxy_class(cls):
        """
        Returns the proxy class. 

        :param config: Config object.
        :type config: bulbs.config.Config

        :rtype: class

        """
        raise NotImplementedError 

    @property
    def _id(self):
        """
        Returns the element ID. 

        :rtype: int or str

        .. note:: This is the element's "primary key"; however, some DBs (such 
                  as neo4j) reuse IDs if they are deleted so be careful with 
                  how you use them. 
      
                  If you want to guarantee they are unique across the DB's 
                  lifetime either don't physically delete elements and just set
                  a deleted flag, or use some other mechanism  for the primary 
                  key, such as an external sequence or a hash.

        """
        return self._result.get_id()

    @property 
    def _type(self):
        """
        Returns the result's base type, either vertex or edge.

        :rtype: str

        """
        return self._result.get_type()

    def _set_pretty_id(self, client):
        """
        Sets the ID var defined in Config as a Python property. Defaults to eid.
        
        :param client: Client object.
        :type client: Client

        :rtype: None

        .. note:: The user-configured element_type and label vars are not set 
                  as Python properties because they are class vars so you set 
                  those when you define the Models.

        """
        pretty_var = client.config.id_var
        fget = lambda self: self._result.get_id()
        setattr(Element, pretty_var, property(fget))                    

    def __setattr__(self, key, value):
        """
        Overloaded to set the object attributes or the property data.

        If you explicitly set/change the values of an element's properties,
        make sure you call save() to updated the values in the DB.

        :param key: Database property key.
        :type key: str

        :param value: Database property value.
        :type value: str, int, long, float, list, dict

        :rtype: None

        """
        # caching __dict__ to avoid the dots and boost performance
        dict_ = self.__dict__ 

        # dict_.get() is faster than getattr()
        _initialized = dict_.get("_initialized", False)

        if key in dict_ or _initialized is False:
            # set the attribute normally
            object.__setattr__(self, key, value)
        else:
            # set the attribute as a data property
            self._data[key] = value

    def __getattr__(self, name):
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
        """
        Returns the number of items stored in the DB results

        :rtype: int

        """
        return len(self._data)

    def __contains__(self, key):
        """
        Returns True if the key in the database property data.
        
        :param key: Property key. 
        :type key: str

        :rtype: bool

        """
        return key in self._data

    def __eq__(self, element):
        """
        Returns True if the elements are equal

        :param element: Element object.
        :type element: Element

        :rtype bool

        """
        return (isinstance(element, Element) and
                element.__class__  == self.__class__ and
                element._id == self._id and
                element._data == self._data)

    def __ne__(self, element):
        """
        Returns True if the elements are not equal.

        :param element: Element object.
        :type element: Element

        :rtype bool

        """
        return not self.__eq__(element)

    def __repr__(self):
        """
        Returns the string representation of the attribute.

        :rtype: unicode

        """
        return self.__unicode__()
    
    def __str__(self):
        """
        Returns the string representation of the attribute.

        :rtype: unicode

        """
        return self.__unicode__()
    
    def __unicode__(self):
        """
        Returns the unicode representation of the attribute.

        :rtype: unicode

        """
        class_name = self.__class__.__name__
        element_uri = self._result.get_uri()
        representation = "<%s: %s>" % (class_name, element_uri)
        return u(representation)    # Python 3

    def __setstate__(self, state):
        config = state['_config']
        client_class = state['_client_class']
        client = client_class(config)
        state['_client'] = client
        state['_vertices'] = VertexProxy(Vertex, client)
        state['_edges'] = EdgeProxy(Edge, client)
        del state['_client_class']
        del state['_config']
        self.__dict__ = state

    def __getstate__(self):
        state = self.__dict__.copy() 
        state['_config'] = self._client.config
        state['_client_class'] = self._client.__class__
        del state['_client']
        del state['_vertices']
        del state['_edges']
        return state
        
    def get(self, name, default_value=None):
        """
        Returns the value of a Python attribute or the default value.

        :param name: Python attribute name.
        :type name: str

        :param default_value: Default value. Defaults to None.
        :type default_value: object

        :rtype: object or None

        """
        # TODO: Why do we need this?
        return getattr(self, name, default_value)


    def data(self):
        """
        Returns the element's property data.

        :rtype: dict

        """
        return self._data

    def map(self):
        """
        Deprecated. Returns the element's property data.

        :rtype: dict

        """
        log.debug("This is deprecated; use data() instead.")
        return self.data()



#
# Vertices
#

class Vertex(Element):
    """
    A container for a Vertex returned by a client proxy.

    :param client: The Client object for the database.
    :type client: Client

    :ivar eid: Element ID. This varname is configurable in Config.
    :ivar _client: Client object.
    :ivar _data: Property data dict returned in Result.
    :ivar _vertices: Vertex proxy object.
    :ivar _edges: Edge proxy object.
    :ivar _initialized: Boolean set to True upon initialization.

    Example::
        
    >>> from bulbs.neo4jserver import Graph
    >>> g = Graph()                   # Create a Neo4j Graph object
    >>> james = g.vertices.get(3)     # Get a vertex from the database
    >>> james.age = 34                # Set a database property
    >>> james.save()                  # Save the vertex in the database
    >>> james.data()                   # Get the database property map
    >>> friends = james.outV("knows") # Return Vertex generator of friends

    """  
    @classmethod
    def get_base_type(cls):
        """
        Returns this element class's base type, which is "vertex". 
        
        :rtype: str
        
        .. admonition:: WARNING 

           Don't override this.

        """
        # Don't override this
        return "vertex"

    @classmethod
    def get_element_key(cls, config):
        """
        Returns the element key. Defaults to "vertex". Override this in Model.

        :param config: Config object.
        :type config: Config

        :rtype: str

        """
        return "vertex"

    @classmethod 
    def get_index_name(cls, config):
        """
        Returns the index name. Defaults to the value of Config.vertex_index. 

        :param config: Config object.
        :type config: Config

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

    def outE(self, label=None, start=None, limit=None):
        """
        Returns the outgoing edges.

        :param label: Optional edge label.
        :type label: str or None

        :rtype: Edge generator

        """
        resp = self._client.outE(self._id, label, start, limit)
        return initialize_elements(self._client,resp)

    def inE(self, label=None, start=None, limit=None):
        """
        Returns the incoming edges.

        :param label: Optional edge label.
        :type label: str or None

        :rtype: Edge generator

        """
        resp = self._client.inE(self._id, label, start, limit)
        return initialize_elements(self._client,resp)

    def bothE(self, label=None, start=None, limit=None):
        """
        Returns the incoming and outgoing edges.

        :param label: Optional edge label.
        :type label: str or None

        :rtype: Edge generator

        """
        resp = self._client.bothE(self._id, label, start, limit)
        return initialize_elements(self._client,resp)

    def outV(self, label=None, start=None, limit=None):
        """
        Returns the out-adjacent vertices.

        :param label: Optional edge label.
        :type label: str or None

        :rtype: Vertex generator

        """
        resp = self._client.outV(self._id, label, start, limit)
        return initialize_elements(self._client,resp)

    def inV(self, label=None, start=None, limit=None):
        """
        Returns the in-adjacent vertices.

        :param label: Optional edge label.
        :type label: str or None

        :rtype: Vertex generator

        """
        resp = self._client.inV(self._id, label, start, limit)
        return initialize_elements(self._client,resp)
        
    def bothV(self, label=None, start=None, limit=None):
        """
        Returns all incoming- and outgoing-adjacent vertices.

        :param label: Optional edge label.
        :type label: str or None

        :rtype: Vertex generator

        """
        resp = self._client.bothV(self._id, label, start, limit)
        return initialize_elements(self._client,resp)

    def save(self):
        """
        Saves the vertex in the database.

        :rtype: Response

        """
        return self._vertices.update(self._id, self._data)
            

class VertexProxy(object):
    """ 
    A proxy for interacting with vertices on the graph database. 

    :param element_class: The element class managed by this proxy instance.
    :type element_class: Vertex class

    :param client: The Client object for the database.
    :type client: Client

    :ivar element_class: Element class.
    :ivar client: Client object.
    :ivar index: The primary index object or None.

    .. note:: The Graph object contains a VertexProxy instance named "vertices".

    Example::
        
    >>> from bulbs.neo4jserver import Graph
    >>> g = Graph()                                  # Create Neo4j Graph
    >>> james = g.vertices.create(name="James")      # Create vertex in DB
    >>> g.vertices.update(james.eid, name="James T") # Update properties
    >>> james = g.vertices.get(james.eid)            # Get vertex (again)
    >>> g.vertices.delete(james.eid)                 # Delete vertex

    """
    def __init__(self,element_class, client):
        assert issubclass(element_class, Vertex)

        self.element_class = element_class
        self.client = client
        self.index = None

        # Add element class to Registry so we can initialize query results.
        self.client.registry.add_class(element_class)

    def create(self, _data=None, **kwds):
        """
        Adds a vertex to the database and returns it.

        :param _data: Optional property data dict.
        :type _data: dict

        :param kwds: Optional property data keyword pairs. 
        :type kwds: dict

        :rtype: Vertex

        """
        data = build_data(_data, kwds)
        resp = self.client.create_vertex(data)
        return initialize_element(self.client, resp.results)

    def get(self, _id):
        """
        Returns the vertex for the given ID.

        :param _id: The vertex ID.
        :type _id: int or str

        :rtype: Vertex or None

        """
        try:
            resp = self.client.get_vertex(_id)
            return initialize_element(self.client, resp.results)
        except LookupError:
            return None
        
    def get_or_create(self, key, value, _data=None, **kwds):
        """
        Lookup a vertex in the index and create it if it doesn't exsit.

        :param key: Index key.
        :type key: str

        :param value: Index value.
        :type value: str, int, long

        :param _data: Optional property data dict.
        :type _data: dict

        :param kwds: Optional property data keyword pairs. 
        :type kwds: dict

        :rtype: Vertex

        """
        # TODO: Make this an atomic Gremlin method
        # TODO: This will only index for non-models if autoindex is True.
        # Relationship Models are set to index by default, but 
        # EdgeProxy doesn't have this method anyway.
        vertex = self.index.get_unique(key, value)
        if vertex is None:
            vertex = self.create(_data, **kwds)
        return vertex

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

        :param _data: Optional property data dict.
        :type _data: dict

        :param kwds: Optional property data keyword pairs. 
        :type kwds: dict

        :rtype: Response

        """ 
        # NOTE: this no longer returns an initialized element because not all 
        # Clients return element data, e.g. Neo4jServer retuns nothing.
        data = build_data(_data, kwds)
        self.client.update_vertex(_id, _data)

    def remove_properties(self, _id):
        """
        Removes all properties from a vertex and returns the response.

        :param _id: The vertex ID.
        :type _id: int or str

        :rtype: Response

        """ 
        return self.client.remove_vertex_properties(_id)
                    
    def delete(self, _id):
        """
        Deletes a vertex from the graph database and returns the response.

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

    :ivar eid: Element ID. This varname is configurable in Config.
    :ivar _client: Client object.
    :ivar _data: Property data dict returned in Result.
    :ivar _vertices: Vertex proxy object.
    :ivar _edges: Edge proxy object.
    :ivar _initialized: Boolean set to True upon initialization.

    Example:
        
    >>> from bulbs.neo4jserver import Graph
    >>> g = Graph()                   # Create a Neo4j Graph
    >>> edge = g.edges.get(8)         # Get an edge from DB

    >>> label = edge.label()          # Return edge label
    >>> outV = edge.outV()            # Return outgoing vertex
    >>> inV = edge.inV()              # Return incoming vertex

    >>> edge._outV                    # Return the outgoing vertex ID
    >>> edge._inV                     # Return the incoming vertex ID

    >>> edge.weight = 0.5             # Set a property
    >>> edge.save()                   # Save properties in DB
    >>> data = edge.data()            # Return property data

    """
    @classmethod
    def get_base_type(cls):
        """
        Returns this element class's base type, which is "edge".
        
        :rtype: str
        
        .. admonition:: WARNING 

           Don't override this.

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
        Returns the edge's outgoing (start) vertex ID.

        :rtype: int

        """
        return self._result.get_outV()
        
    @property
    def _inV(self):
        """
        Returns the edge's incoming (end) vertex ID.

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
        Returns the outgoing (start) Vertex of the edge.

        :rtype: Vertex

        """
        return self._vertices.get(self._outV)
    
    def inV(self):
        """
        Returns the incoming (end) Vertex of the edge.

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
        Saves the edge in the database.

        :rtype: Response

        """
        return self._edges.update(self._id, self._data)

    
class EdgeProxy(object):
    """ 
    A proxy for interacting with edges on the graph database. 

    :param element_class: The element class managed by this proxy instance.
    :type element_class: Edge class

    :param client: The Client object for the database.
    :type client: Client

    :ivar element_class: Element class
    :ivar client: Client object.
    :ivar index: The primary index object or None.

    .. note:: The Graph object contains an EdgeProxy instance named "edges".

    Example::
        
    >>> from bulbs.neo4jserver import Graph
    >>> g = Graph()                                   # Create Neo4j Graph
    >>> james = g.vertices.create(name="James")       # Create vertex
    >>> julie = g.vertices.create(name="Julie")       # Create vertex
    >>> knows = g.edges.create(james, "knows", julie) # Create edge
    >>> knows = g.edges.get(knows.eid)                # Get edge (again)
    >>> g.edges.update(knows.eid, weight=0.5)         # Update properties
    >>> g.edges.delete(knows.eid)                     # Delete edge

    """
    def __init__(self, element_class, client):
        assert issubclass(element_class, Edge)

        self.element_class = element_class
        self.client = client
        self.index = None

        # Add element class to Registry so we can initialize query results.
        self.client.registry.add_class(element_class)

    def create(self, outV, label, inV, _data=None, **kwds):
        """
        Creates an edge in the database and returns it.
        
        :param outV: The outgoing vertex. 
        :type outV: Vertex or int
                      
        :param label: The edge's label.
        :type label: str

        :param inV: The incoming vertex. 
        :type inV: Vertex or int

        :param _data: Optional property data dict.
        :type _data: dict

        :param kwds: Optional property data keyword pairs. 
        :type kwds: dict

        :rtype: Edge

        """ 
        assert label is not None
        data = build_data(_data, kwds)
        outV, inV = coerce_vertices(outV, inV)
        resp = self.client.create_edge(outV, label, inV, data)
        return initialize_element(self.client, resp.results)

    def get(self,_id):
        """
        Retrieves an edge from the database and returns it.

        :param _id: The edge ID.
        :type _id: int or str

        :rtype: Edge or None

        """
        try:
            resp = self.client.get_edge(_id)
            return initialize_element(self.client, resp.results)
        except LookupError:
            return None

    def get_all(self):
        """
        Returns all the edges in the graph.
        
        :rtype: Edge generator
 
        """
        resp = self.client.get_all_edges()
        return initialize_elements(self.client, resp)


    def update(self,_id, _data=None, **kwds):
        """ 
        Updates an edge in the database and returns it. 
        
        :param _id: The edge ID.
        :type _id: int or str

        :param _data: Optional property data dict.
        :type _data: dict

        :param kwds: Optional property data keyword pairs. 
        :type kwds: dict

        :rtype: Response

        """
        # NOTE: this no longer returns an initialized element because 
        # not all Clients return element data, e.g. Neo4jServer retuns nothing.
        data = build_data(_data, kwds)
        return self.client.update_edge(_id, data)
                    
    def remove_properties(self, _id):
        """
        Removes all properties from a element and returns the response.
        
        :param _id: The edge ID.
        :type _id: int or str

        :rtype: Response
        
        """
        return self.client.remove_edge_properties(_id)

    def delete(self, _id):
        """
        Deletes a vertex from a graph database and returns the response.
        
        :param _id: The edge ID.
        :type _id: int or str

        :rtype: Response

        """
        return self.client.delete_edge(_id)


#
# Element Utils
#

def build_data(_data, kwds):
    """
    Returns property data dict, regardless of how it was entered.

    :param _data: Optional property data dict.
    :type _data: dict

    :param kwds: Optional property data keyword pairs. 
    :type kwds: dict

    :rtype: dict

    """
    # Doing this rather than defaulting the _data arg to a mutable value
    data = {} if _data is None else _data
    data.update(kwds)
    return data

def coerce_vertices(outV, inV):
    """
    Coerces the outgoing and incoming vertices to integers or strings.

    :param outV: The outgoing vertex. 
    :type outV: Vertex or int
                      
    :param inV: The incoming vertex. 
    :type inV: Vertex or int

    :rtype: tuple

    """
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



