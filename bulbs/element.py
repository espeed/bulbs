# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Vertex and Edge container classes and proxies.

"""
from utils import initialize_element, initialize_elements

def get_base_type(element_class):
    if issubclass(element_class,Vertex):
        base_type = "vertex"
    elif issubclass(element_class,Edge):
        base_type = "edge"
    else:
        raise TypeError("%s is not an Element class" % element_class)
    return base_type


class Element(object):
    """This is an abstract base class for Vertex and Edge"""
    
    def __init__(self,resource):
        # NOTE: Put all the init stuff in initialize_element() because 
        # Model() calls it explicitly instead of super().__init__()
        #self._initialize_element(resource,result)
        self._resource = resource

    def _initialize(self,result):
        # Reource object and Result object
        self._result = result
        self._set_pretty_vars(self._resource)
        self._vertices = VertexProxy(Vertex,self._resource)
        self._edges = EdgeProxy(Edge,self._resource)
        #print "TTTTT", type(self._resource)
 
    @property
    def _id(self):
        return self._result.get_id()

    @property 
    def _type(self):
        return self._result.get_type()

    #
    # First Thing: Fix this self.__class__ should be self but it breaks stuff
    # property must be set on the class, not the object
    #

    def _set_pretty_vars(self,resource):
        self._set_python_property(resource.config.id_var,"_id")
        # this won't work b/c element_type and label are set as class vars
        #self._set_python_property(resource.config.type_var,"_type")
        #self._set_python_property(resource.config.label_var,"_label")

    def _set_python_property(self,pretty_var,ugly_var):
        fget = lambda x: getattr(self,ugly_var)
        setattr(self.__class__,pretty_var,property(fget))                    

    def __getattr__(self,attribute):
        try:
            return self._result.data[attribute]
        except:
            raise AttributeError("%s is not defined and is not in Result data" % attribute)

    def __len__(self):
        return len(self._result.data)

    def __contains__(self, item):
        return item in self._result.data

    def __eq__(self, obj):
        return (hasattr(obj, "__class__") and
                self.__class__ == obj.__class__ and
                hasattr(self, "_result") and 
                hasattr(obj, "_result") and
                self._result.get_id() == obj._result.get_id() and
                self._result.data == obj._result.data
                )

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __repr__(self):
        return self.__unicode__()
    
    def __str__(self):
        return self.__unicode__()
    
    def __unicode__(self):
        return u"<%s: %s>" % (self.__class__.__name__,self._result.get_uri())

    def map(self):
        """Returns a dict of the element's data that's stored in the DB."""
        return self._result.data


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


class VertexProxy(object):
    """ A proxy for interacting with vertices on Rexster. """

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
        """Retrieves an element from Rexster and returns it."""
        #print "TYPE", type(self.resource)
        try:
            resp = self.resource.get_vertex(_id)
            return initialize_element(self.resource,resp.results)
        except LookupError:
            return None
        
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
    
    def remove_properties(self,_id):
        """Removes all properties from a element and returns the response.""" 
        return self.resource.remove_vertex_properties(_id)
    
    # Why is this here???
    #def create_index(self,name,index_class,**kwds):
    #    resp = self.resource.create_vertex_index(name,**kwds)
    #    return index_class(self.resource,resp.results)


class EdgeProxy(object):
    """ A proxy for interacting with edges on Rexster. """

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
        """Retrieves an element from Rexster and returns it."""
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
  

    # Why is this here???
    #def create_index(self,name,index_class,**kwds):
    #    resp = self.resource.create_edge_index(name,**kwds)
    #    return index_class(self.resource,resp.results)

    def _coerce_vertex_id(self,v):
        """Returns the vertex ID coerced into an int if need be."""
        # param v is either a Vertex object or a vertex ID.
        # the vertex ID may have been passed in as a string
        if isinstance(v,Vertex):
            vertex_id = v._id
        else:
            # using corece_id to support linked-data URI IDs
            vertex_id = self._coerce_id(v)
        return vertex_id

    def _coerce_id(_id):
        # try to coerce the element ID string to an int.
        # ORIENTDB USES STRINGS SO THIS WON'T WORK FOR IT
        try:
            return int(_id)
        except:
            return _id
