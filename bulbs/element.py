# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Vertex and Edge container classes and associated proxy classes.

"""
from utils import initialize_element, initialize_elements


class Element(object):
    """
    An abstract base class for Vertex and Edge containers.

    :param resource: The Resource object for the database.
    :type resource: Resource

    """
    _class_type = None

    def __init__(self,resource):
        self._resource = resource
        self._data = {}

    def _initialize(self,result):
        # initialize all non-database properties here because
        # __setattr__ will assume all non-defined properties are database properties
        self._result = result
        self._data = result.get_map().copy()
        self._set_pretty_id(self._resource)
        self._vertices = VertexProxy(Vertex,self._resource)
        self._edges = EdgeProxy(Edge,self._resource)
        self._initialized = True
       
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

    def _set_pretty_id(self, resource):
        """
        Sets the ID var specified in Config as a Python property. Defaults to eid.
        
        The user-configured element_type and label vars are not set because 
        they are class vars so you set those when you create the Model.

        """
        pretty_var = resource.config.id_var
        fget = lambda x: self._result.get_id()
        setattr(self.__class__,pretty_var,property(fget))                    

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
        return u"<%s: %s>" % (self.__class__.__name__,self._result.get_uri())

    def map(self):
        """
        Returns the element's property data.

        :rtype: dict

        """
        return self._data


class Vertex(Element):
    """
    A container for a Vertex returned by a resource proxy.

    Example::
        
    >>> from bulbs.neo4jserver import Graph
    >>> g = Graph()
    >>> james = g.vertices.create({'name':'James'})
    >>> julie = g.vertices.create({'name':'Julie'})
    >>> g.edges.create(james,"knows",julie)
    >>> james.outE()
    >>> james.outE('knows')
    >>> james.outV()
    >>> james.outV('knows')
    >>> james.age = 34
    >>> james.save()

    """  


    @classmethod
    def get_base_type(cls):
        #: Don't override this
        return "vertex"

    @classmethod
    def get_element_key(cls, config):
        return cls.get_base_type()

    @classmethod 
    def get_index_name(cls, config):
        return config.vertex_index

    @classmethod 
    def get_proxy_class(cls):
        return VertexProxy

    def outE(self,label=None):
        """
        Returns the outgoing edges of the vertex.

        :param label: An optional edge label.
        :type label: str or None

        :rtype: Edge generator

        """
        resp = self._resource.outE(self._id,label)
        return initialize_elements(self._resource,resp)

    def inE(self,label=None):
        """
        Returns the incoming edges of the vertex.

        :param label: An optional edge label.
        :type label: str or None

        :rtype: Edge generator

        """
        resp = self._resource.inE(self._id,label)
        return initialize_elements(self._resource,resp)

    def bothE(self,label=None):
        """
        Returns the incoming and outgoing edges of the vertex.

        :param label: An optional edge label.
        :type label: str or None

        :rtype: Edge generator

        """
        resp = self._resource.bothE(self._id,label)
        return initialize_elements(self._resource,resp)

    def outV(self,label=None):
        """
        Returns the out-adjacent vertices of the vertex.

        :param label: An optional edge label.
        :type label: str or None

        :rtype: Vertex generator

        """
        resp = self._resource.outV(self._id,label)
        return initialize_elements(self._resource,resp)

    def inV(self,label=None):
        """
        Returns the in-adjacent vertices of the vertex.

        :param label: An optional edge label.
        :type label: str or None

        :rtype: Vertex generator

        """
        resp = self._resource.inV(self._id,label)
        return initialize_elements(self._resource,resp)
        
    def bothV(self,label=None):
        """
        Returns all incoming- and outgoing-adjacent vertices of vertex.

        :param label: An optional edge label.
        :type label: str or None

        :rtype: Vertex generator

        """
        resp = self._resource.bothV(self._id,label)
        return initialize_elements(self._resource,resp)

    def save(self):
        """
        Saves the vertex on the resource.

        :rtype: Response

        """
        return self._vertices.update(self._id, self._data)
    

class Edge(Element):
    """
    A container for an Edge returned by a resource proxy.

    :param resource: The Resource object for the database.
    :type resource: Resource

    Example::
        
    >>> from bulbs.neo4jserver import Graph
    >>> g = Graph()
    >>> james = g.vertices.create({'name':'James'})
    >>> julie = g.vertices.create({'name':'Julie'})
    >>> knows = g.edges.create(james,"knows",julie)
    >>> knows.outV()
    >>> knows._outV
    >>> knows.inv()
    >>> knows._inV
    >>> knows._label
    >>> knows.weight = 0.5
    >>> knows.save()
    >>> knows.map()

    """

    @classmethod
    def get_base_type(cls):
        #: Don't override this
        return "edge"

    @classmethod
    def get_element_key(cls, config):
        return cls.get_base_type()

    @classmethod 
    def get_index_name(cls, config):
        return config.edge_index

    @classmethod 
    def get_proxy_class(cls):
        return EdgeProxy

    @property
    def _outV(self):
        """Returns the outgoing vertex ID of the edge."""
        return self._result.get_outV()
        
    @property
    def _inV(self):
        """Returns the incoming vertex ID of the edge."""
        return self._result.get_inV()
        
    @property
    def _label(self):
        """Returns the edge's label."""
        return self._result.get_label()
        
    def outV(self):
        """Returns the outgoing Vertex of the edge."""
        return self._vertices.get(self._outV)
    
    def inV(self):
        """Returns the incoming Vertex of the edge."""
        return self._vertices.get(self._inV)

    def save(self):
        """Saves the edge on the resource."""
        return self._edges.update(self._id, self._data)


class VertexProxy(object):
    """ 
    A proxy for interacting with vertices on the Resource. 

    :param element_class: The element class to be managed by this proxy instance.
    :type element_class: Vertex or Edge class

    :param resource: The Resource object for the database.
    :type resource: Resource

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

    def __init__(self,element_class,resource):
        assert issubclass(element_class,Vertex)
        self.element_class = element_class
        self.resource = resource
        self.resource.registry.add_class(element_class)
        self.index = None

    def create(self,data={}):
        """
        Adds a vertex to the database and returns it.

        :param data: A dict containing the vettex's property data.
        :type data: dict

        :rtype: Vertex

        """
        resp = self.resource.create_vertex(data)
        return initialize_element(self.resource,resp.results)

    def get(self,_id):
        """
        Returns the vertex for the given ID.

        :param _id: The vertex ID.
        :type _id" int or str

        :rtype: Vertex

        """
        try:
            resp = self.resource.get_vertex(_id)
            return initialize_element(self.resource,resp.results)
        except LookupError:
            return None
        
    # is this really needed?
    def get_all(self):
        """
        Returns all the vertices in the graph.
        
        :rtype: Vertex generator
 
        """
        resp = self.resource.get_all()
        return intialize_elements(self.resource,resp)

    def update(self,_id,data):
        """
        Updates an element in the graph DB and returns it.

        :param _id: The vertex ID.
        :type _id: int or str

        :rtype: Response

        """ 
        # NOTE: this no longer returns an initialized element because not all 
        # Resources return element data, e.g. Neo4jServer retuns nothing.
        self.resource.update_vertex(_id,data)

    # is this really needed?    
    def remove_properties(self,_id):
        """
        Removes all properties from a vertex and returns the response.

        :param _id: The vertex ID.
        :type _id: int or str

        :rtype: Response

        """ 
        return self.resource.remove_vertex_properties(_id)
                    
    def delete(self,_id):
        """
        Deletes a vertex from a graph DB and returns the response.

        :param _id: The vertex ID.
        :type _id: int or str

        :rtype: Response
        
        """
        return self.resource.delete_vertex(_id)


class EdgeProxy(object):
    """ 
    A proxy for interacting with edges on the Resource. 

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

    def __init__(self,element_class,resource):
        assert issubclass(element_class,Edge)
        self.element_class = element_class
        self.resource = resource
        self.resource.registry.add_class(element_class)
        self.index = None

    def create(self,outV,label,inV,data={}):
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
        outV = self._coerce_vertex_id(outV)
        inV = self._coerce_vertex_id(inV)
        resp = self.resource.create_edge(outV,label,inV,data)
        return initialize_element(self.resource,resp.results)

    def get(self,_id):
        """
        Retrieves an edge from the database and returns it.

        :param _id: The edge ID.
        :type _id: int or str

        :rtype: Edge

        """
        try:
            resp = self.resource.get_edge(_id)
            return initialize_element(self.resource,resp.results)
        except LookupError:
            return None

    def update(self,_id,data):
        """ 
        Updates an edge in the database and returns it. 
        
        :param _id: The edge ID.
        :type _id: int or str

        :param data: A dict containing the edge's property data.
        :type data: dict

        :rtype: Response

        """
        # NOTE: this no longer returns an initialized element because 
        # not all Resources return element data, e.g. Neo4jServer retuns nothing.
        return self.resource.update_edge(_id,data)
                    
    def remove_properties(self,_id):
        """
        Removes all properties from a element and returns the response.
        
        :param _id: The edge ID.
        :type _id: int or str

        :rtype: Response
        
        """
        return self.resource.remove_edge_properties(_id)

    def delete(self,_id):
        """
        Deletes a vertex from a graph DB and returns the response.
        
        :param _id: The edge ID.
        :type _id: int or str

        :rtype: Response

        """
        return self.resource.delete_edge(_id)
  
    def _coerce_vertex_id(self,v):
        """
        Coerces an object into a vertex ID and returns it.

        :param v: The object we want to coerce into a vertex ID.
        :type v: Vertex object or vertex ID.

        :rtype: int or str

        """
        if isinstance(v,Vertex):
            vertex_id = v._id
        else:
            # the vertex ID may have been passed in as a string
            # using corece_id to support OrientDB and linked-data URI (non-integer) IDs
            vertex_id = self._coerce_id(v)
        return vertex_id

    def _coerce_id(_id):
        """
        Tries to coerce a vertex ID into an integer and returns it.

        :param v: The vertex ID we want to coerce into an integer.
        :type v: int or str

        :rtype: int or str

        """
        try:
            return int(_id)
        except:
            # some DBs, such as OrientDB, use string IDs
            return _id
