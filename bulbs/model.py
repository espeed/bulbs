# -*- coding: utf-8 -*-
# 
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Base classes for modeling domain objects that wrap vertices and edges.

"""

import config
from rest import Resource
from index import IndexProxy
from element import Vertex, VertexProxy, Edge, EdgeProxy
from typesystem import TypeSystem, ClassProperty

class Model(TypeSystem):
    """
    Abstract base class for Node and Relationship.

    It's a sublcass of TypeSystem, which provides a mechanism for type-checking
    database properties before they're saved in the database.

    To create a type-checked database property, use the Property class and
    datatype classes, which are located in the property module. Example::

        name = Property(String, nullable=False)
        age = Property(Integer)

    """

    # You can override this default resource.
    resource = Resource(config.DATABASE_URL)

    @property
    def eid(self):
        """Return the element ID. Override this to change it from eid."""
        return self._id
 
    #@property
    #def element_type(self):
    #    """Return the element type."""
    #    return self._data.get(config.TYPE_VAR,None)
        #return self._data[TYPE_VAR]


    @classmethod
    def get(self,_id):
        """
        Returns the element for the specified ID.

        ::param _id: The element's ID.

        """
        return self._element_proxy.get(_id)

    @classmethod
    def get_all(self):
        """Returns all the elements for the model type."""
        index_name = self._element_proxy._path()
        target = "%s/indices/%s" % (self.resource.db_name,index_name)
        params = dict(key="element_type",value=self.element_type)
        resp = self.resource.get(target,params)
        for result in resp.results:
            yield self(self.resource,result)

    @classmethod 
    def remove(self,_id,params):
        """
        Removes a property from the element for the specified ID.

        ::param _id: The element's ID.

        ::param params: The element's property to remove.

        """
        return self._element_proxy.remove(_id,params)

    @classmethod
    def create_index(self,index_keys=None,index_type="automatic"):
        """
        Creates an index for the model.

        ::param index_keys: The specific keys to index. If set to None,
                            any key can be indexed. Defaults to None.

        ::param index_type: The type of index to create. Either manual
                            or automatic. Defaults to automatic. See
                            Rexster docs for definitions.
        """
        index_name = self._get_index_name()
        index_class = self._get_index_class()
        index_attributes = (index_name,index_class,index_type,index_keys)
        return self.index_proxy.create(*index_attributes)

    @classmethod
    def delete_index(self):
        """Deletes the model's index."""
        index_name = self._get_element_key()
        return self.index_proxy.delete(index_name)

    @classmethod 
    def _get_element_proxy(self):
        """
        Returns the element's proxy class. The Node and Relationship classes
        override this.

        """
        raise NotImplementedError

    @classmethod 
    def _get_index_proxy(self):
        """Returns the index's proxy class."""
        return IndexProxy(self.resource,self)


    @classmethod
    def _get_index_name(self):
        """Returns the model's index name."""
        return self._get_element_key()

    @classmethod
    def _get_index(self):
        """Returns the model's index."""
        index_name = self._get_index_name()
        return self.index_proxy.get(index_name)

    index = ClassProperty(_get_index)
    index_proxy = ClassProperty(_get_index_proxy)


    #def element_type_sanity_check(self,results):
    #    element_type = self.get_element_type(results)
    #    if element_type is not None:
    #        if element_type != getattr(self,TYPE_VAR):
    #            raise("DB element type (%) doesn't match class element type (%s)" % \
    #                      (element_type, getattr(self,TYPE_VAR)))

    #def get_arg(self,name,default=None):
    #    return self._kwds.get(name,default)

    def _create(self,*args,**kwds):
        """
        Create a new element in the database.
        
        ::param *args: Optional dict of name/value pairs of database properties.
        ::param **kwds: name/value pairs of database properties to store.
        """
        self._set_keyword_attributes(kwds)
        self._validate_property_data()
        data = self._get_property_data()
        args = list(args)
        args.append(data)
        self.before_created()
        # Using super here b/c Vertex and Edge have different create methods
        #resp = super(self.__class__,self).create(*args,raw=True)
        # got a "mismatched input, expecting double star" in Jython so
        # passing raw as a "double star"
        kwds = dict(raw=True)
        resp = self._element_proxy.create(*args,**kwds)
        self._initialize_element(self.resource,resp.results)
        #self.set_element_data(resp.results)
        self.after_created()
        
    def _read(self,results):
        """
        Read an element's data that was retrieved from the DB and set its model 
        values.

        ::param results: A list containing the results returned by Rexster.

        """
        self.before_read()
        self._initialize_element(self.resource,results)
        #self.set_element_data(results)
        self._set_property_data(results)
        self.after_read()

    def _update(self,eid,kwds):
        """
        Updates the element in the database.

        ::param eid: The ID of the element to update.
        ::param **kwds: name/value pairs of database properties to store.

        """
        self.eid = eid
        self._set_keyword_attributes(kwds)
        self.save()

    def save(self):
        """
        Saves/updates the element's data in the database.
        
        """
        self._validate_property_data()
        data = self._get_property_data()        
        self.before_updated()
        #resp = super(self.__class__,self).update(self.eid,data,raw=True)
        resp = self._element_proxy.update(self.eid,data,raw=True)
        self._initialize_element(self.resource,resp.results)
        #self.set_element_data(resp.results)
        self.after_updated()

    def delete(self):
        """Deletes an element from the database."""
        # Should we make this a classmethod instead?
        # Should we provide an option to set a deleted flag or just override this?
        self.before_deleted()
        #resp = super(self.__class__,self).delete(self)
        resp = self._element_proxy.delete(self)
        self.after_deleted()
        return resp

    def initialize(self,args,kwds):
        """
        Initialize the model.

        If results is passed in, that means data was retrieved from the DB
        via a get request or gremlin query so we just set the property values
        based on what is stored in the DB.

        If eid was passed in, that means we're updating the element so we
        set the model's attributes based on the keyword variables passed in,
        and we save in the DB any attributes specified as DB Properties.

        If neither results nor eid were passed in, that means we're creating a
        new element so we set the model's attributes based on the keyword
        variables that were passed in, and we save in the DB any attributes
        specified as DB Properties.

        Also, we set self.kwds so the vars are available to the before/after wrappers.
        
        ::param *args: Optional dict of name/value pairs of database properties.

        ::param **kwds: name/value pairs of database properties to store.

        """
        # We're doing a little arg dance instead of keyword mangling.
        # This avoids problems if a user wants to use the word "results" as a
        # Property name (actually, no it doesn't, b/c you're using results
        # elsewhere. Ugh -- I hate keyword mangling.
        _id = None
        results = None
        args = list(args)

        # save kwds so it's available to before/after wrappers
        self._kwds = kwds      

        # in case someone wants to pass in a dict of data instead of by keywords
        _data = kwds.pop("_data",{})

        # in case someone passed in a dict of data plus some data by keywords
        _data.update(**kwds)
      
        if args and isinstance(args[0],Resource):
            self.resource = args.pop(0)            
        if args and isinstance(args[0],dict):
            results = args.pop(0)            
        if args and isinstance(args[0],int):
            _id = args.pop(0)            

        #print "RESULTS:", results

        self.before_initialized()
        if results is not None:
            # must have been a get or gremlin request
            Model._read(self,results)
        elif _id is not None:
            # calling Model explicitly b/c Vertex/Edge have an update method too
            Model._update(self,_id,_data)
        elif args or kwds:
            # calling Model explicitly b/c Vertex/Edge have a create method too
            Model._create(self,*args,**_data)
        else:
            # create an empty Node (can't have an empty Relationship b/c must have label)
            Model._create(self,{})
        self.after_initialized()


    def before_initialized(self):
        """Virtual method run before the model is initialized."""
        pass

    def after_initialized(self):
        """Virtual method run after the model is initialized."""
        pass

    def before_created(self):
        """Virtual method run before an element is created in the DB."""
        pass

    def after_created(self):
        """Virtual method run after an element is created in the DB."""
        pass

    def before_read(self):
        """Virtual method run before element data is read from the DB."""
        pass

    def after_read(self):
        """Virtual method run after element data is read from the DB."""
        pass

    def before_updated(self):
        """Virtual method run before an element is updated in the DB."""
        pass

    def after_updated(self):
        """Virtual method run after an element is updated in the DB."""
        pass

    def before_deleted(self):
        """Virtual method run before an element is deleted from the DB."""
        pass

    def after_deleted(self):
        """Virtual method run after an element is deleted from the DB."""
        pass
 

class Node(Vertex,Model):
    """ 
    An abstract base class used to create classes that model domain objects. It is
    not meant to be used directly

    To use this, create a subclass specific to the type of data you are 
    storing. 

    Example model declaration::

        from bulbs.model import Node
        from bulbs.property import Property, String, Integer

        class Person(Node):
            element_type = "person"

            name = Property(String, nullable=False)
            age = Property(Integer)

            def after_created():
                # include code to create relationships and to index the node
                pass

   Example usage::

        # Create a node in the DB:
        >>> james = Person(name="James Thornton")
        >>> james.eid
        3
        >>> james.name
        'James Thornton'

        # Get a node from the DB:
        >>> james = Person.get(3)

        # Update the node in the DB:
        >>> james.age = 34
        >>> james.save()

   """

    # IMPORTANT:
    # Can't do the metamagic unless object has been created so we can't use 
    # __new__ because all the initialzed vars would be on the class and not the
    # object. Don't worry about setting the object attributes for the kwds data
    # because the initialize sets them and the grandancestor Element provides 
    # DB data to you by overriding __getattr__.

    #element_type = "node"

    def __init__(self,*args,**kwds):
        """
        Initialize the node.

        ::param *args: Optional dict of name/value pairs of database properties.
        ::param **kwds: name/value pairs of database properties to store.

        """
        # pass results as the first (and only) arg to init values from gets
        # pass eid as the first arg if you are updating the element
        self.initialize(args,kwds)

    @classmethod
    def _get_element_key(self):
        """Returns the element's key that's used for stuff like the index name."""
        element_key = getattr(self,config.TYPE_VAR)
        return element_key

    @classmethod 
    def _get_index_class(self):
        """Returns the element's base class."""
        return "vertex"

    @classmethod
    def _get_element_proxy(self):
        """Returns the element's proxy."""
        return VertexProxy(self.resource,self)

    _element_proxy = ClassProperty(_get_element_proxy)

class Relationship(Edge,Model):
    """ 
    An abstract base class used to create classes that model domain objects. It is
    not meant to be used directly

    To use this, create a subclass specific to the type of data you are 
    storing. 

    Example usage for an edge between a blog entry node and its creating user::

        class CreatedBy(Relationship):
            label = "created_by"

            timestamp = Property(Float, default="current_timestamp", nullable=False)

            @property
            def entry(self):
                return Entry.get(self.outV)

            @property
            def user(self):
                return User.get(self.inV)
        
            def current_timestamp(self):
                return time.time()

          >>> entry = Entry(text="example blog entry")
          >>> james = Person(name="James")
          >>> CreatedBy(entry,james)
      
          # Or if you just want to create a basic relationship between two nodes, do::
          >>> Relationship.create(entry,"created_by",james)

    """

    def __init__(self,*args,**kwds):
        args = list(args)
        if args and isinstance(args[1],Vertex):
            # 2nd arg is a Vertex so they're in form of CreatedBy(entry,james)
            # TODO: clean up this arg thing -- this is a quick hack to fix a bug
            outV = args.pop(0)
            inV = args.pop(0) 
            args = (outV,self.label,inV)
        self.initialize(args,kwds)
    
    @classmethod
    def create(self,outV,label,inV,**kwds):
        """
        Create a generic relationship between two nodes.

        ::param outV: the outgoing vertex.
        ::param label: the edge's label.
        ::param inV: the incoming vertex.
        ::param **kwds: Optional keyword arguments. Name/value pairs of properties to store.
        """
        return Relationship(outV,label,inV,**kwds)
        
    @classmethod
    def _get_element_key(self):
        """Returns the element's key that's used for stuff like the index name."""
        return self.label

    @classmethod 
    def _get_index_class(self):
        """Returns the element's base class."""
        return "edge"

    @classmethod
    def _get_element_proxy(self):
        """Returns the element's proxy."""
        return EdgeProxy(self.resource,self)

    _element_proxy = ClassProperty(_get_element_proxy)




    
    
    
