# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Vertex and Edge container classes and associated proxy classes to interact with
Rexster.

"""
import utils
from gremlin import Gremlin

class Element(object):
    """This is an abstract base class for Vertex and Edge"""
    
    def __init__(self,resource,results):
        """
        Initializes an element after it is added, updated, or retrieved from 
        the database.

        :param resource: The Resource object for the database.

        :param results: The results list returned by Rexster.
        
        """
        # NOTE: Put all the init stuff in initialize_element() because 
        # Model() calls it explicitly instead of super().__init__()
        self._initialize_element(resource,results)

    def _initialize_element(self,resource,results):
        """
        Initialize the element's resource, _data, and Gremlin proxy. This is
        called explicitly by Element.__init__ and Model.__init__

        :param resource: The Resource object for the database.

        :param results: The results list returned by Rexster.

        """
        self._data = {}
        self.resource = resource
        self._set_element_data(results)
        self._gremlin = Gremlin(self.resource)

    def _set_element_data(self,results):
        """ 
        Set the elements data returned by the DB.

        :param results: The results list returned by Rexster.
     
        """
        self._data = results
 
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
            raise AttributeError("%s not found and not in self._data" \
                                     % (attribute))

    def __len__(self):
        """Returns the number of items stored in the DB results"""
        return len(self._data)

    def __contains__(self, item):
        """Returns True if attribute is a key that has been stored in the DB"""
        return item in self._data

    def __eq__(self, obj):
        """Returns True if the elements are equal"""
        return (hasattr(obj, "_id")
                and self._id == obj._id
                and hasattr(obj, "_data")
                and self._data == obj._data
                and hasattr(obj, "__class__")
                and self.__class__ == obj.__class__
                )

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
        #return u"<Rexster %s %s: %s>" % \
        #    (self.resource.db_name, self.__class__.__name__, self._id)
        return u"<%s: %s>" % (self.__class__.__name__,
                              self._proxy(self.resource)._uri(self._id))

    @property
    def _id(self):
        """
        Returns the element ID. This is the element's "primary key"; however,
        some DBs (such as neo4j) reuse IDs if they are deleted so 
        be careful with how you use them. If you want to guarantee
        they are unique across the DB's lifetime either don't 
        physically delete elements and just set a deleted flag, or
        use some other mechanism, such as an external sequence or 
        a hash.
        
        """
        #int(self._data['_id'])
        return utils.coerce_id(self._data['_id'])

    @property
    def _type(self):
        """Returns the _type set by Rexster: either vertex, edge, or index."""
        return self._data['_type']

    @property
    def _proxy(self):
        """Returns the element's proxy to Rexster."""
        proxy_map = dict(vertex=VertexProxy,edge=EdgeProxy)
        return proxy_map[self._type]

    @property
    def map(self):
        """Returns a dict of the element's data that's stored in the DB."""
        private_keys = ['_id','_type','_outV','_inV','_label']
        map_ = dict()
        for key, value in self._data.items():
            if key not in private_keys:
                map_.update({key:value})
        return map_

    def gremlin(self,script,*classes,**kwds):
        """
        Returns a generator containing the results of the Gremlin script. 
        Remember you can always use the list() function to turn an iterator or 
        a generator into a list. Sometimes it's useful to turn a generator into
        a list when doing unittests or when you want to check how many items 
        are in the results.
       
        :param script: Gremlin script to send to Rexster. Since this begins 
                       from the context of an element instead of a graph, the 
                       script should begin with the reference to itself 
                       (v or e) instead of a reference to the graph (g). 
                       Example:

                       .. code-block:: groovy

                       // do this... 
                       v.outE('created') 
                        
                       // instead of... 
                       g.v(1).outE('created')
        :param classes: Zero or more subclasses of Element to use when 
                          initializing the the elements returned by the query. 
                          For example, if Person is a subclass of Node (which 
                          is defined in model.py and is a subclass of Vertex), 
                          and the query returns person elements, pass in the 
                          Person class and the method will use the element_type
                          defined in the class to initialize the returned items
                          to a Person object.
        :keyword return_keys: Optional keyword param. A comma-separated list of
                              keys (DB properties) to return. If set to None, it
                              returns all properties. Defaults to None.
        :keyword raw: Optional keyword param. If set to True, it won't try to 
                      initialize data. Defaults to False. 

        :rtype: Generator of items. The data types of the items returned vary 
                depending on the query.

        Example::
       
        >>> from bulbs.graph import Graph()
        >>> g = Graph()
        >>> james = g.vertices.get(3) 
        >>> script = "v.outE('knows').inV"
        >>> results = james.gremlin(script)


        """
        # TODO: now that we're using a proxy, should we always include the 
        # calling class in the class_map?
        return_keys = kwds.pop('return_keys',None)
        raw = kwds.pop('raw',False)
        class_map = dict(vertex=Vertex,edge=Edge)
        kwds = dict(default_class_map=class_map,return_keys=return_keys,raw=raw)
        return self._gremlin._element_query(self,script,*classes,**kwds)


class Vertex(Element):
    """
    A container for Vertex elements returned by Rexster.

    :param resource: The Resource object for the database.
    :param results: The element data returned by Rexster.

    Example::
        
    >>> from bulbs.graph import Graph
    >>> from whybase.person import Person
    >>> g = Graph()
    >>> g.inV(Person,label="knows")

    """     
  
            
    def outE(self,*args,**kwds):
        """
        Return the outgoing edges of the vertex.

        :arg classes: Zero or more classes to used for initializing the 
                        objects returned in the query results.

        :keyword label: Optional. The edge label. Defaults to None.
                        
        :keyword return_keys: Optional. A comman-separated list of
                              keys (DB properties) to return. If set to None, it
                              returns all properties. Defaults to None.

        :param raw: Optional keyword param. If set to True, it won't try to 
                    initialize data. Defaults to False. 

        """
        label, classes = self._parse_args(*args)
        script = "v.outE(%s)" % utils.quote(label)
        return self.gremlin(script,*classes,**kwds)

    def inE(self,*args,**kwds):
        """
        Return the incoming edges of the vertex.


        :param classes: Zero or more classes to used for initializing the 
                          objects returned in the query results.

        :param kwds: name/value pairs of optional arguments:

        :param label: Optional keyword param. The edge label.
                        
        :param return_keys: Optional keyword param. A comman-separated list of
                             keys (DB properties) to return. If set to None, it
                             returns all properties. Defaults to None.

        :param raw: Optional keyword param. If set to True, it won't try to 
                     initialize data. Defaults to False. 
        """
        label, classes = self._parse_args(*args)
        script = "v.inE(%s)" % utils.quote(label)
        return self.gremlin(script,*classes,**kwds)

    def bothE(self,*args,**kwds):
        """
        Return all incoming and outgoing edges of the vertex.

        :param classes: Zero or more classes to used for initializing the 
                         objects returned in the query results.

        :param kwds: name/value pairs of optional arguments:

        :param label: Optional keyword param. The edge label.
                        
        :param return_keys: Optional keyword param. A comman-separated list of
                             keys (DB properties) to return. If set to None, it
                             returns all properties. Defaults to None.

        :param raw: Optional keyword param. If set to True, it won't try to 
                     initialize data. Defaults to False. 
        """
        label, classes = self._parse_args(*args)
        script = "v.bothE(%s)" % utils.quote(label)
        return self.gremlin(script,*classes,**kwds)

    def outV(self,*args,**kwds):
        """ 
        Return the out-adjacent vertices to the vertex.

        :param classes: Zero or more classes to used for initializing the 
                        objects returned in the query results.

        :param kwds: name/value pairs of optional arguments:

        :param label: Optional keyword param. The edge label.
                        
        :param return_keys: Optional keyword param. A comman-separated list of
                             keys (DB properties) to return. If set to None, it
                             returns all properties. Defaults to None.

        :param raw: Optional keyword param. If set to True, it won't try to 
                     initialize data. Defaults to False. 
        """
        label, classes = self._parse_args(*args)
        script = "v.out(%s)" % utils.quote(label)
        return self.gremlin(script,*args,**kwds)
        
    def inV(self,*args,**kwds):
        """
        Return the in-adjacent vertices of the vertex.

        :param classes: Zero or more classes to used for initializing the 
                        objects returned in the query results.

        :param kwds: name/value pairs of optional arguments:

        :param label: Optional keyword param. The edge label.
                        
        :param return_keys: Optional keyword param. A comman-separated list of
                            keys (DB properties) to return. If set to None, it
                            returns all properties. Defaults to None.

        :param raw: Optional keyword param. If set to True, it won't try to 
                     initialize data. Defaults to False. 
        """
        label, classes = self._parse_args(*args)
        script = "v.in(%s)" % utils.quote(label)
        return self.gremlin(script,*classes,**kwds)
        
    def bothV(self,*args,**kwds):
        """
        Return all incoming- and outgoing-adjacent vertices of vertex.

        :param label: Optional, first positional arg. The edge label.

        :param classes: Optional, first or second positional arg.
                        Zero or more classes to used for initializing the 
                        objects returned in the query results.

        :param kwds: name/value pairs of optional arguments:


                        
        :param return_keys: Optional keyword param. A comman-separated list of
                             keys (DB properties) to return. If set to None, it
                             returns all properties. Defaults to None.

        :param raw: Optional keyword param. If set to True, it won't try to 
                     initialize data. Defaults to False. 
        """ 
        label, classes = self._parse_args(*args)
        script = "v.both(%s)" % utils.quote(label)
        return self.gremlin(script,*classes,**kwds)
            
    def get_edges(self,direction,label):
        """
        Returns a generator containing the the edges attached to the vertex 
        that have the specified label and direction. This is a native Rexster 
        query and does not go through Gremlin, and because it doesn't have the 
        compile-time overhead that Gremlin does, it's somewhat faster.

        However, it does not a mechanism for initializing edges to Edge
        subclasses -- everything is returned as a generic Edge object.
        
        :param direction: The direction of edges: Either inE, outE, or bothE.

        :param label: The edges' label. 

        """
        assert direction in ('inE','outE','bothE')
        target = "%s/%s/%s" % (self._base_target(),self._id, direction)
        params = None
        if label: 
            params = dict(_label=label)
        resp = self.resource.get(target,params)           
        for result in resp.results:
            yield Edge(result)

    def _parse_args(self,*args):
        args = list(args)
        label = None
        classes = []
        if args:
            if isinstance(args[0], basestring):
                label = args.pop(0)
        if args:
            classes = args
        return label, classes
    
    def _base_target(self):
        "Returns the base target URL path for vertices on Rexster."""
        base_target = "%s/%s" % (self.resource.db_name,"vertices")
        return base_target

        
class Edge(Element):
    """A container for Edge elements returned by Rexster."""

    @property
    def _outV(self):
        """Returns the outgoing vertex ID of the edge."""
        #return int(self._data['_outV'])
        return utils.coerce_id(self._data['_outV'])
        
    @property
    def _inV(self):
        """Returns the incoming vertex ID of the edge."""
        #return int(self._data['_inV'])
        return utils.coerce_id(self._data['_inV'])

    # TODO: Make outV and inV return a specific Model class and not a generic 
    # Vertex
    @property
    def outV(self):
        """Returns the outgoing Vertex of the edge."""
        return VertexProxy(self.resource).get(self._outV)
    
    @property
    def inV(self):
        """Returns the incoming Vertex of the edge."""
        return VertexProxy(self.resource).get(self._inV)
    
    @property
    def label(self):
        """Returns the edge's label."""
        return self._label


class ElementProxy(object):
    """An abstract base class for VertexProxy and EdgeProxy."""
    
    def __init__(self,resource,element_class):
        """
        Initializes the proxy object.

        :param resource: The Resource object for the database.

        :param element_class: The container class for the element type
                               used to instantiate the element object. 

        """
        self.resource = resource
        self.element_class = element_class

    def _base_target(self):
        base_target = "%s/%s" % (self.resource.db_name,self._path())
        return base_target

    def _uri(self,_id):
        """
        Returns the URI of the element.

        :param _id: The element ID.

        """
        uri = "%s/%s/%s" % (self.resource.db_url,self._path(),_id)
        return uri

    def create(self,data,raw=False):
        """ 
        Adds an element to the database and returns it. 

        :param data: The element's property data to store.

        :param raw: Optional keyword param. If raw is False (which is the 
                     default) it will try to instantiated the element to the 
                     element_class specified when the proxy object was created.
                     However, if the raw param is set to True, it will won't 
                     instantiate the object and will return the raw Response 
                     object.
        """
        target = self._base_target()
        resp = self.resource.post(target,data)
        if raw is True:
            return resp
        # TODO: implement a version for model that returns self()
        return self.element_class(self.resource,resp.results)

    def update(self,_id,data,raw=False):
        """ 
        Updates a vertex in the graph DB and returns it. 
        
        :param _id: The element ID.

        :param data: The element's property data to store.

        :param raw: Optional keyword param. If raw is False (which is the 
                     default) it will try to instantiated the element to the 
                     element_class specified when the proxy object was created.
                     However, if the raw param is set to True, it will won't 
                     instantiate the object and will return the raw Response 
                     object.
        """
        target = "%s/%s" % (self._base_target(),_id)
        resp = self.resource.post(target,data)
        if raw is True:
            return resp
        return self.element_class(self.resource,resp.results)

    def get(self,_id,raw=False):
        """ 
        Retrieves an element from Rexster and returns it. 
        
        :param _id: The ID of the element you want to retrieve.

        :param raw: Optional keyword param. If raw is False (which is the 
                    default) it will try to instantiate the element to the 
                    element_class specified when the proxy object was created.
                    However, if the raw param is set to True, it will won't 
                    instantiate the object and will return the raw Response 
                    object.
        """
        target = "%s/%s" % (self._base_target(),_id)
        resp = self.resource.get(target,params=None)
        if raw is True:
            return resp
        if resp.results:
            return self.element_class(self.resource,resp.results)        
    
    def get_all(self):
        """Returns all the elements from the Rexster of _type vertex or edge."""
        resp = self.resource.get(self._base_target(),params=None)
        for result in resp.results:
            yield self.element_class(self.resource,result)
            
    def remove(self,_id,params):
        """ 
        Removes properties from a vertex and returns the response.

        :param _id: The ID of the element.

        :param params: The properties you want to remove.
        """ 
        # shouldn't this return the updated vertex instead?
        if params is None:
            raise Exception("params are required.")
        target = "%s/%s" % (self._base_target(),_id)
        resp = self.resource.delete(target,params)
        return resp

    def delete(self,element):
        """ 
        Deletes a vertex from a graph DB and returns the response.
        
        :param element: The element you want to delete.
        """
        # TODO: Why are we requiring the full element and not just the ID?
        target = "%s/%s" % (self._base_target(),element._id)
        resp = self.resource.delete(target,params=None)
        return resp


class VertexProxy(ElementProxy):
    """ A proxy for interacting with vertices on Rexster. """

    def __init__(self,resource,element_class=Vertex):
        """
        Initializes the proxy object.

        :param resource: The Resource object for the database.

        :param element_class: A subclass of Vertex used to instantiate objects.

        """
        assert issubclass(element_class,Vertex)
        ElementProxy.__init__(self,resource,element_class)

    @classmethod
    def _path(self):
        """Returns Rexster's URL path segment used for vertices."""
        return "vertices"


class EdgeProxy(ElementProxy):
    """ A proxy for interacting with edges on Rexster. """

    def __init__(self,resource,element_class=Edge):
        """
        :param resource: The Resource object for the database.

        :param element_class: A subclass of Edge used to instantiate objects.

        """
        assert issubclass(element_class,Edge)
        ElementProxy.__init__(self,resource,element_class)

    def create(self,outV,label,inV,data={},raw=False):
        """ 
        Adds an edge to the database and returns it. 

        :param outV: The outgoing vertex. You can pass the vertex in as either
                      an ID or a Vertex object, and it will automatically 
                      convert it to an ID for you.
 
        :param label: The edge's label.

        :param inV: The incoming vertex. You can pass the vertex in as either 
                     an ID or a Vertex object, and it will automatically 
                     convert it to an ID for you.

        :param data: The edge's property data to save in the database.
        
        :param raw: Optional keyword param. If raw is False (which is the 
                     default) it will try to instantiated the element to the 
                     element_class specified when the proxy object was created.
                     However, if the raw param is set to True, it will won't 
                     instantiate the object and will return the raw Response 
                     object.
        """
        assert label is not None
        outV = self._coerce_vertex_id(outV)
        inV = self._coerce_vertex_id(inV)
        edge_data = dict(_outV=outV,_label=label,_inV=inV)
        data.update(edge_data)
        return ElementProxy.create(self,data,raw)

    def _path(self):
        """Returns Rexster's URL path segment used for edges."""
        return "edges"
    
    def _coerce_vertex_id(self,v):
        """ 
        Returns the vertex ID coerced into an int if need be.

        :param v: Either a Vertex object or a vertex ID.

        """
        if isinstance(v,Vertex):
            vertex_id = v._id
        else:
            # the vertex ID may have been passed in as a string
            #vertex_id = int(v)
            vertex_id = utils.coerce_id(v)
        return vertex_id

  
