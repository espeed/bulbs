# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Vertex and Edge container and proxy classes.

"""
from utils import initialize_element, initialize_elements

class Element(object):
    """An abstract base class for Vertex and Edge containers."""
    
    def __init__(self,resource):
        self._resource = resource
        self._data = {}

    def _initialize(self,result):
        self._result = result
        self._data = result.get_map().copy()
        self._set_pretty_id(self._resource)
        self._vertices = VertexProxy(Vertex,self._resource)
        self._edges = EdgeProxy(Edge,self._resource)
        self._set_initialized(True)

    def _set_initialized(self,value=True):
        self._initialized = value
       
    @property
    def _id(self):
        """
        Returns the element ID. This is the element's "primary key"; however,
        some DBs (such as neo4j) reuse IDs if they are deleted so be careful 
        with how you use them. If you want to guarantee they are unique across 
        the DB's lifetime either don't physically delete elements and just set 
        a deleted flag, or use some other mechanism, such as an external 
        sequence or a hash.

        """
        return self._result.get_id()

    @property 
    def _type(self):
        """Returns the element's base type, either vertex or edge."""
        return self._result.get_type()

    def _set_pretty_id(self, resource):
        """
        Sets the ID var specified in Config. Defaults to eid.
        
        The user-configured element_type and label vars are not set because 
        they are class vars so you set those when you create the Model.

        """
        pretty_var = resource.config.id_var
        fget = lambda x: self._result.get_id()
        setattr(self.__class__,pretty_var,property(fget))                    

    def __setattr__(self, key, value):
        _initialized = getattr(self,"_initialized",False)
        if _initialized is True:
            self._data[key] = value
        else:
            super(Element,self).__setattr__(key, value)

    def __getattr__(self,attribute):
        """
        Returns the value stored in the DB if the property hasn't been 
        set explicitly. 

        If you explicitly set/change the values of an element's properties,
        make sure you call save() to updated the values in the DB.

        """
        try:
            return self._data[attribute]
        except:
            raise AttributeError(attribute)

    def __len__(self):
        return len(self._data)

    def __contains__(self, item):
        return item in self._data

    def __eq__(self, obj):
        return (hasattr(obj, "__class__") and
                self.__class__ == obj.__class__ and
                self._id == obj._id and
                self._data == obj._data)

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __repr__(self):
        return self.__unicode__()
    
    def __str__(self):
        return self.__unicode__()
    
    def __unicode__(self):
        return u"<%s: %s>" % (self.__class__.__name__,self._result.get_uri())

    def map(self):
        """Returns a dict of the element's data."""
        return self._data


class Vertex(Element):
    """A container for Vertex elements returned by the resource."""     
         
    def outE(self,label=None):
        """Return the outgoing edges of the vertex."""
        resp = self._resource.outE(self._id,label)
        return initialize_elements(self._resource,resp)

    def inE(self,label=None):
        """Return the incoming edges of the vertex."""
        resp = self._resource.inE(self._id,label)
        return initialize_elements(self._resource,resp)

    def bothE(self,label=None):
        """Return all incoming and outgoing edges of the vertex."""
        resp = self._resource.bothE(self._id,label)
        return initialize_elements(self._resource,resp)

    def outV(self,label=None):
        """Return the out-adjacent vertices to the vertex."""
        resp = self._resource.outV(self._id,label)
        return initialize_elements(self._resource,resp)

    def inV(self,label=None):
        """Return the in-adjacent vertices of the vertex."""
        resp = self._resource.inV(self._id,label)
        return initialize_elements(self._resource,resp)
        
    def bothV(self,label=None):
        """Return all incoming- and outgoing-adjacent vertices of vertex."""
        resp = self._resource.bothV(self._id,label)
        return initialize_elements(self._resource,resp)

    def save(self):
        self._vertices.update(self._id, self._data)
    

class Edge(Element):
    """A container for Edge elements returned by the resource."""

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
        
    # TODO: Make outV and inV return a specific Model, not a generic Vertex. - Done! :)
    def outV(self):
        """Returns the outgoing Vertex of the edge."""
        return self._vertices.get(self._outV)
    
    def inV(self):
        """Returns the incoming Vertex of the edge."""
        return self._vertices.get(self._inV)

    def save(self):
        self._edges.update(self._id, self._data)

class VertexProxy(object):
    """ A proxy for interacting with vertices on the Resource. """

    def __init__(self,element_class,resource):
        assert issubclass(element_class,Vertex)
        self.element_class = element_class
        self.resource = resource
        self.resource.registry.add_class(element_class)
        self.index = None

    def create(self,data={}):
        """Adds an element to the database and returns it."""
        resp = self.resource.create_vertex(data)
        return initialize_element(self.resource,resp.results)

    def get(self,_id):
        """Retrieves an element from the database and returns it."""
        try:
            resp = self.resource.get_vertex(_id)
            return initialize_element(self.resource,resp.results)
        except LookupError:
            return None
        
    # is this really needed?
    def get_all(self):
        # for this 
        resp = self.resource.get_all()
        return intialize_elements(self.resource,resp)

    def update(self,_id,data):
        """Updates an element in the graph DB and returns it.""" 
        # NOTE: this no longer returns an initialized element because not all 
        # Resources return element data, e.g. Neo4jServer retuns nothing.
        return self.resource.update_vertex(_id,data)
                    
    def delete(self,_id):
        """Deletes a vertex from a graph DB and returns the response."""
        return self.resource.delete_vertex(_id)

    # is this really needed?    
    def remove_properties(self,_id):
        """Removes all properties from a element and returns the response.""" 
        return self.resource.remove_vertex_properties(_id)
    
class EdgeProxy(object):
    """ A proxy for interacting with edges on the Resource. """

    def __init__(self,element_class,resource):
        assert issubclass(element_class,Edge)
        self.element_class = element_class
        self.resource = resource
        self.resource.registry.add_class(element_class)
        self.index = None

    def create(self,outV,label,inV,data={}):
        """Adds an edge to the database and returns it.""" 
        assert label is not None
        outV = self._coerce_vertex_id(outV)
        inV = self._coerce_vertex_id(inV)
        resp = self.resource.create_edge(outV,label,inV,data)
        return initialize_element(self.resource,resp.results)

    def get(self,_id):
        """Retrieves an element from the Resource and returns it."""
        try:
            resp = self.resource.get_edge(_id)
            return initialize_element(self.resource,resp.results)
        except LookupError:
            return None

    def update(self,_id,data):
        # NOTE: this no longer returns an initialized element because not all 
        # Resources return element data, e.g. Neo4jServer retuns nothing.
        return self.resource.update_edge(_id,data)
                    
    def delete(self,_id):
        """Deletes a vertex from a graph DB and returns the response."""
        return self.resource.delete_edge(_id)

    def remove_properties(self,_id):
        """Removes all properties from a element and returns the response."""
        return self.resource.remove_edge_properties(_id)
  
    def _coerce_vertex_id(self,v):
        """Returns the vertex ID coerced into an int if need be."""
        # param v is either a Vertex object or a vertex ID.
        # the vertex ID may have been passed in as a string
        if isinstance(v,Vertex):
            vertex_id = v._id
        else:
            # using corece_id to support OrientDB and linked-data URI (non-integer) IDs
            vertex_id = self._coerce_id(v)
        return vertex_id

    def _coerce_id(_id):
        # Try to coerce the element ID string to an int,
        # but some resources, such as OrientDB, use string IDs
        try:
            return int(_id)
        except:
            return _id
