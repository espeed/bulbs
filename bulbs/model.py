# -*- coding: utf-8 -*-
# 
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Base classes for modeling domain objects that wrap vertices and edges.

"""
from bulbs.property import Property
from bulbs.element import Element, Vertex, VertexProxy, Edge, EdgeProxy, coerce_vertices
from bulbs.utils import initialize_element, get_one_result, get_logger, extract

# Model Modes
DEFAULT = 1
STRICT = 2

log = get_logger(__name__)


class ModelMeta(type):
    """Metaclass used to set database Property definitions on Models"""

    def __init__(cls, name, base, namespace):
        # store the Property definitions on the class as a dictionary 
        # mapping the Property key to the Property instance
        cls._properties = cls._get_initial_properties()
        cls._register_properties(namespace)

    def _get_initial_properties(cls):
        # Get Properties defined in the parent and inherit them.
        # Or if the Model doesn't have a parent Model, set it to an empty dict
        properties = {}
        parent_properties = getattr(cls, '_properties', None)
        if parent_properties:
            properties = parent_properties.copy() 
        return properties
            
    def _register_properties(cls, namespace):
        # loop through the class namespace looking for database Property instances
        # e.g. age = Integer()
        for key, value in namespace.items():
            assert key not in cls._properties, "Can't redefine Property '%s'" % key
            if isinstance(value, Property):
                property_instance = value  # for clarity
                cls._properties[key] = property_instance
                cls._set_property_name(key,property_instance)
                cls._set_property_attribute(key,property_instance)
                # not doing this b/c some Properties are calculated at savetime
                #delattr(cls, key) 
                
    def _set_property_name(cls, key, property_instance):
        """Set the Property name; use the attribute name unless explicitly set via kwd param."""
        if property_instance.name is None:
            property_instance.name = key
            
    def _set_property_attribute(cls, key, property_instance):
        """Set the Model class attribute based on the Property definition."""
        if property_instance.default is not None:
            # The value entered could be a scalar or a method name in the model
            property_value = cls._get_property_default(key, property_instance)
        elif property_instance.fget:
            # wrapped fset and fdel in str() to make the default None work with getattr
            fget = getattr(cls, property_instance.fget)
            fset = getattr(cls, str(property_instance.fset), None)
            fdel = getattr(cls, str(property_instance.fdel), None)
            property_value = property(fget, fset, fdel)
        else:
            property_value = None
        setattr(cls, key, property_value)

    def _get_property_default(cls, key, property_instance):
        # The value entered could be a scalar or a method name in the model
        default_value = property_instance.default
        fget = getattr(cls, default_value, None)
        if fget is not None:
            # The default_value is the name of a method defined in the Model
            default_value = property(fget)
        return default_value


class Model(object):

    __metaclass__ = ModelMeta

    _mode = DEFAULT

    def __setattr__(self, key, value):
        if key in self._properties:
            # we want Model Properties to be set be set as actual attributes
            # because they can be real Python propertes or calculated values,
            # which are calcualted/set upon each save().
            value = self._coerce_property_value(key, value)
            object.__setattr__(self, key, value)
        else:
            Element.__setattr__(self, key, value)

    def _instantiate(self, args, kwds):
        self._set_keyword_attributes(kwds)

    def _coerce_property_value(self, key, value):
        if value is not None:
            property_instance = self._properties[key]
            value = property_instance.coerce(key, value)
        return value

    def _set_keyword_attributes(self, kwds):
        for key, value in kwds.iteritems():
            # Notice that __setattr__ is overloaded
            setattr(self, key, value)

    def _set_property_data(self):
        """
        Sets Property data when an element is being initialized, after it is
        retrieved from the DB -- we set it to None if it won't set.        
        """
        type_system = self._resource.type_system
        for key, property_instance in self._properties.items():
            # Convert the Properties to the defined data types and then 
            # update the self._data values that were initially set by Element._initialize()
            # Actually, no we're not, we're bypassing setattr, but will this work for 
            # Python properties that don't have an fset?
            #if property_instance.default is not None:
            #    # for now, don't set read-only vars
            #    continue
            name = property_instance.name
            value = self._data.get(key, None)
            value = property_instance.convert_to_python(type_system, value)
            # TODO: think through this some more...
            if property_instance.fset is None:
                self._data[key] = value
            else:
                # Notice that __setattr__ is overloaded so bypassing it
                object.__setattr__(self, key, value)
        
    def _get_property_data(self):
        """Returns validated Property data, ready to be saved in the DB."""
        data = self._get_initial_data()
        type_var = self._resource.config.type_var
        type_system = self._resource.type_system
        if hasattr(self, type_var):
            # add element_type to the database properties to be saved;
            # but don't worry about "label", it's always saved on the edge
            data[type_var] = getattr(self, type_var)
        for key, property_instance in self._properties.items():
            value = getattr(self, key)
            property_instance.validate(key, value)
            name = property_instance.name
            value = property_instance.convert_to_db(type_system, value)
            data[key] = value
        return data

    def _get_initial_data(self):
        """Returns empty dict if mode is set to strict, else return the existing _data."""
        if self._mode == STRICT:
            data = {}
        else:
            data = self._data.copy()
        return data

    def _get_index(self, index_name):
        """Returns an index for the given name if it's stored in the Registery."""
        try:
            index = self._resource.registry.get_index(index_name)
        except KeyError:
            index = None
        return index


class Node(Vertex,Model):
    """ 
    An abstract base class used to create classes that model domain objects. It is
    not meant to be used directly

    To use this, create a subclass specific to the type of data you are storing. 

    Example model declaration::

        from bulbs.model import Node
        from bulbs.property import String, Integer

        class Person(Node):
            element_type = "person"
            
            name = String(nullable=False)
            age = Integer()

    Example usage::

        >>> from person import Person
        >>> from bulbs.neo4jserver import Graph
        >>> g = Graph()

        # Add a proxy interface to the Graph object for the Person Model:
        >>> g.add_proxy("people", Person)

        # Create a Person node, which automatically saves it in the database:
        >>> james = g.people.create(name="James Thornton")
        >>> james.eid
        3
        >>> james.name
        'James Thornton'

        # Get the node (again) from the database by its element ID:
        >>> james = g.people.get(james.eid)

        # Update the node and save it in the database:
        >>> james.age = 34
        >>> james.save()

        # Lookup people using the Person Model's primary index:
        >>> nodes = g.people.index.lookup(name="James Thornton")
        
    """
    @classmethod
    def get_element_type(cls, config):
        element_type = getattr(cls, config.type_var)
        return element_type

    @classmethod
    def get_element_key(cls, config):
        return cls.get_element_type(config)

    @classmethod 
    def get_index_name(cls, config):
        return cls.get_element_type(config)

    @classmethod 
    def get_proxy_class(cls):
        return NodeProxy

    def _initialize(self, result):
        # this is called by the initialize_element util; 
        # putting it here to ensure method resolution order.
        # initialize all non-DB properties here
        Vertex._initialize(self,result)
        self._initialized = False
        self._set_property_data()
        self._initialized = True
        
    def save(self):
        """Saves/updates the element's data in the database."""
        data = self._get_property_data()
        index_name = self.get_index_name(self._resource.config)
        return self._resource.update_indexed_vertex(self._id, data, index_name)
        
    #:
    #: Override the _create and _update methods to cusomize behavior.
    #:
        
    def _create(self, args, kwds):  
        self._instantiate(args, kwds)
        data = self._get_property_data()
        index_name = self.get_index_name(self._resource.config)
        resp = self._resource.create_indexed_vertex(data, index_name)
        result = get_one_result(resp)  
        self._initialize(result)
        
    def _update(self, _id, kwds):
        self._instantiate(kwds)
        data = self._get_property_data()
        index_name = self.get_index_name(self._resource.config)
        resp = self._resource.update_indexed_vertex(data, index_name)
        result = get_one_result(resp)  
        self._initialize(result)
        

class Relationship(Edge,Model):
    """ 
    An abstract base class used to create classes that model domain objects. It is
    not meant to be used directly

    To use this, create a subclass specific to the type of data you are 
    storing. 

    Example usage for an edge between a blog entry node and its creating user::

        class Knows(Relationship):
            label = "knows"

            timestamp = Float(default="current_timestamp", nullable=False)

            def current_timestamp(self):
                return time.time()

    Example usage::

          >>> from person import Person, Knows
          >>> from bulbs.neo4jserver import Graph
          >>> g = Graph()

          # Add proxy interfaces to the Graph object for each custom Model:
          >>> g.add_proxy("people", Person)
          >>> g.add_proxy("knows", Knows)

          # Create two Person nodes, which are automatically saved in the database:
          >>> james = g.people.create(name="James")
          >>> julie = g.people.create(name="Julie")

          # Create a "knows" relationship between James and Julie:
          >>> knows = g.knows.create(james,julie)
          >>> knows.timestamp

          # Get the people James knows (the outgoing vertices labeled "knows")
          >>> friends = james.outV('knows')

    """
    @classmethod
    def get_label(cls, config):
        label = getattr(cls, config.label_var)
        return label

    @classmethod
    def get_element_key(cls, config):
        #if cls.__name__ == "Relationship":
        #    return "relationship"
        return cls.get_label(config)

    @classmethod 
    def get_index_name(cls, config):
        return cls.get_label(config)

    @classmethod 
    def get_proxy_class(cls):
        return RelationshipProxy

    def _initialize(self,result):
        # this is called by initialize_element; 
        # putting it here to ensure method resolution order
        # initialize all non-DB properties here
        Edge._initialize(self,result)
        self._initialized = False
        self._set_property_data()
        self._initialized = True

    def save(self):
        """Saves/updates the element's data in the database."""
        data = self._get_property_data()      
        return self._resource.update_edge(self._id, data)
        
    #
    # Override the _create and _update methods to customize behavior.
    #

    def _create(self, outV, inV, args, kwds):
        self._instantiate(args, kwds)
        label = self.get_label(self._resource.config)
        data = self._get_property_data()
        outV, inV = coerce_vertices(outV, inV)
        resp = self._resource.create_edge(outV, label, inV, data)
        result = get_one_result(resp)
        self._initialize(result)
        
    def _update(self, _id, data):
        self._instantiate(args, kwds)
        data = self._get_property_data()
        resp = self._resource.update_edge(_id, data)
        result = get_one_result(resp)
        self._initialize(result)


class NodeProxy(VertexProxy):

    def create(self, *args, **kwds):
        node = self.element_class(self.resource)
        node._create(args, kwds)
        return node
        
    def update(self, _id, *args, **kwds):
        node = self.element_class(self.resource)
        node._update(_id, args, kwds)
        return node

    def get_all(self):
        """Returns all the elements for the model type."""
        config = self.resource.config
        type_var = config.type_var
        element_type = self.element_class.get_element_type(config)
        return self.index.lookup(type_var,element_type)


class RelationshipProxy(EdgeProxy):

    def create(self, outV, inV, *args, **kwds):
        relationship = self.element_class(self.resource)
        relationship._create(outV, inV, args, kwds)
        return relationship

    def update(self, _id, *args, **kwds):
        relationship = self.element_class(self.resource)
        relationship._update(_id, args, kwds)
        return relationship

    def get_all(self):
        """Returns all the relationships for the label."""
        # TODO: find a blueprints method that returns all edges for a given label
        # because you many not want to index edges
        config = self.resource.config
        label_var = config.label_var
        label = self.element_class.get_label(config)
        return self.index.lookup(label_var,label)
        
