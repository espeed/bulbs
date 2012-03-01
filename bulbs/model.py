# -*- coding: utf-8 -*-
# 
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Base classes for modeling domain objects that wrap vertices and edges.

"""
import six   # Python 3
import inspect
import types
from collections import OrderedDict, Callable

from bulbs.property import Property
from bulbs.element import Element, Vertex, VertexProxy, Edge, EdgeProxy, coerce_vertices, build_data
from bulbs.utils import initialize_element, get_one_result, get_logger, extract
import bulbs.utils as utils

# Model Modes
DEFAULT = 1
STRICT = 2

log = get_logger(__name__)


class Bundle(OrderedDict):
    
    def as_tuple(self):
        return tuple(self.values())


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
        for key in namespace: # Python 3
            value = namespace[key]
            assert key not in cls._properties, "Can't redefine Property '%s'" % key
            if isinstance(value, Property):
                property_instance = value  # for clarity
                cls._properties[key] = property_instance
                cls._set_property_name(key,property_instance)
                cls._initialize_property(key,property_instance)
                # not doing this b/c some Properties are calculated at savetime
                #delattr(cls, key) 
                            
    def _set_property_name(cls, key, property_instance):
        """Set the Property name; use the attribute name unless explicitly set via kwd param."""
        if property_instance.name is None:
            property_instance.name = key

    def _initialize_property(cls, key, property_instance):
        """Set the Model class attribute based on the Property definition."""
        if property_instance.fget:
            # this is a calculated property (should it persist?) -- TODO: make this configurable
            # wrapped fset and fdel in str() to make the default None not error on getattr
            fget = getattr(cls, property_instance.fget)
            fset = getattr(cls, str(property_instance.fset), None)
            fdel = getattr(cls, str(property_instance.fdel), None)
            property_value = property(fget, fset, fdel)
        else:
            property_value = None
        setattr(cls, key, property_value)


class Model(six.with_metaclass(ModelMeta, object)):  # Python 3

    _mode = DEFAULT
    
    # TODO: Why must this be here and in Node?
    def __setattr__(self, key, value):
        return self._setattr(key, value)

    # overloaded in Node and Relationship to deal with multiple inheritence
    def _setattr(self, key, value):
        if key in self._properties:
            #print "KEY", key
            # we want Model Properties to be set be set as actual attributes
            # because they can be real Python propertes or calculated values,
            # which are calcualted/set upon each save().
            value = self._coerce_property_value(key, value)
            object.__setattr__(self, key, value)
        else:
            Element.__setattr__(self, key, value)


    def _coerce_property_value(self, key, value):
        if value is not None:
            property_instance = self._properties[key]
            value = property_instance.coerce(key, value)
        return value

    def _set_property_defaults(self):
        for key in self._properties:
            default_value = self._get_property_default(key)     
            Model.__setattr__(self, key, default_value)
            
    def _get_property_default(self, key):
        # The value entered could be a scalar or a function name
        # TODO: make this work for model methods?
        # defer the call until all properties are set? Or only for calculated properties?
        property_instance = self._properties[key]
        default_value = property_instance.default
        if isinstance(default_value, Callable):
            default_value = default_value()
        return default_value

    def _set_keyword_attributes(self, _data, kwds):
        # may have passed in keys that are not defined as Properties
        data = build_data(_data, kwds)
        for key in data: # Python 3
            value = data[key]  # 
            # Notice that __setattr__ is overloaded
            # Must explicitly use Model's setattr because of multiple inheritence 
            Model.__setattr__(self, key, value)

    def _set_property_data(self):
        """
        Sets Property data when an element is being initialized, after it is
        retrieved from the DB -- we set it to None if it won't set.        
        """
        type_system = self._client.type_system
        for key in self._properties: # Python 3
            property_instance = self._properties[key]
            name = property_instance.name
            value = self._data.get(key, None)
            # what about fset and fget values?
            value = property_instance.convert_to_python(type_system, key, value)
            # TODO: Maybe need to wrap this in try/catch too
            object.__setattr__(self, key, value)
            
    def _get_property_data(self):
        """Returns validated Property data, ready to be saved in the DB."""
        data = self._get_initial_data()
        type_var = self._client.config.type_var
        type_system = self._client.type_system
        if hasattr(self, type_var):
            # add element_type to the database properties to be saved;
            # but don't worry about "label", it's always saved on the edge
            data[type_var] = getattr(self, type_var)
        for key in self._properties:  # Python 3
            property_instance = self._properties[key]
            value = self._get_property_value(key)
            property_instance.validate(key, value)
            #name = property_instance.name
            value = property_instance.convert_to_db(type_system, value)
            data[key] = value
        return data

    def _get_property_value(self, key):
        value = getattr(self, key)
        if isinstance(value, Callable):
            return value()
        return value

    def _get_initial_data(self):
        """Returns empty dict if mode is set to strict, else return the existing _data."""
        data = {} if self._mode == STRICT else self._data.copy()
        return data

    def _map(self):
        # map() is overloaded in Node and Relationship so calculated props are returned properly. 
        # Calculated props shouldn't be stored, but their components should be.
        data = dict()
        # Iterating over self._properties instead of _data like in Element
        # in case new props have been set but not saved   
        for key in self._properties: 
            data[key] = getattr(self, key)
        return data

    def get_index(self, index_name):
        """Returns an Index in the Registery or None."""
        try:
            index = self._client.registry.get_index(index_name)
        except KeyError:
            index = None
        return index

    def get_index_keys(self):
        # Defaults to None (index all keys)
        return None

    def get_property_keys(self):
        return self._properties.keys()

    def get_bundle(self, _data=None, **kwds):
        # It's just on save that you don't set Property defaults.
        # You can here because they will be overridden by set_keyword_attributes.
        self._set_property_defaults()   
        self._set_keyword_attributes(_data, kwds)
        # Bundle is an OrderedDict with a custom as_tuple() method, so order matters
        bundle = Bundle()
        bundle['data'] = self._get_property_data()
        bundle['index_name'] = self.get_index_name(self._client.config)
        bundle['keys'] = self.get_index_keys()
        return bundle

        


class Node(Vertex,Model):
    """ 
    Node is a Vertex model. It's an abstract base class used to create classes 
    that model domain objects. It's not meant to be used directly.

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

        # Add a "people" proxy to the Graph object for the Person model:
        >>> g.add_proxy("people", Person)

        # Use it to create a Person node, which also saves it in the database:
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

        # Lookup people using the Person model's primary index:
        >>> nodes = g.people.index.lookup(name="James Thornton")
        
    """
    def __setattr__(self, key, value):
        Model._setattr(self, key, value)

    # TODO: Sure we want this?
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

    def map(self):
        """
        Returns the Model's property data.

        :rtype: dict

        """
        return self._map()


    def save(self):
        """Saves/updates the element's data in the database."""
        data = self._get_property_data()
        index_name = self.get_index_name(self._client.config)
        keys = self.get_index_keys()
        self._client.update_indexed_vertex(self._id, data, index_name, keys)
        
    #:
    #: Override the _create and _update methods to cusomize behavior.
    #:
    
    def _create(self, _data, kwds):  
        # bundle is an OrderedDict containing data, index_name, and keys
        data, index_name, keys = self.get_bundle(_data, **kwds).as_tuple()
        result = self._client.create_indexed_vertex(data, index_name, keys).one()
        self._initialize(result)
        
    def _update(self, _id, _data, kwds):
        data, index_name, keys = self.get_bundle(_data, **kwds).as_tuple()
        result = self._client.update_indexed_vertex(_id, data, index_name, keys).one()
        self._initialize(result)
        
    def _initialize(self, result):
        # this is called by the initialize_element util; 
        # putting it here to ensure method resolution order.
        # initialize all non-DB properties here
        Vertex._initialize(self,result)
        self._initialized = False
        self._set_property_data()
        self._initialized = True


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
    def __setattr__(self, key, value):
        Model._setattr(self, key, value)


    @classmethod
    def get_label(cls, config):
        label = getattr(cls, config.label_var)
        return label

    @classmethod
    def get_element_key(cls, config):
        return cls.get_label(config)

    @classmethod 
    def get_index_name(cls, config):
        return cls.get_label(config)

    @classmethod 
    def get_proxy_class(cls):
        return RelationshipProxy

    def map(self):
        """
        Returns the Model's property data.

        :rtype: dict

        """
        return self._map()


    def save(self):
        """Saves/updates the element's data in the database."""
        data = self._get_property_data()      
        self._client.update_edge(self._id, data)

    #
    # Override the _create and _update methods to customize behavior.
    #

    def _create(self, outV, inV, _data, kwds):
        label = self.get_label(self._client.config)
        outV, inV = coerce_vertices(outV, inV)
        data, index_name, keys = self.get_bundle(_data, **kwds).as_tuple()
        result = self._client.create_edge(outV, label, inV, data).one()
        self._initialize(result)
        
    def _update(self, _id, _data, kwds):
        data, index_name, keys = self.get_bundle(_data, **kwds).as_tuple()
        result = self._client.update_edge(_id, data).one()
        self._initialize(result)

    def _initialize(self,result):
        # this is called by initialize_element; 
        # putting it here to ensure method resolution order
        # initialize all non-DB properties here
        Edge._initialize(self,result)
        self._initialized = False
        self._set_property_data()
        self._initialized = True


class NodeProxy(VertexProxy):

    # make these have the same signature as VertexProxy

    def create(self, _data=None, **kwds):
        node = self.element_class(self.client)
        node._create(_data, kwds)
        return node
        
    def update(self, _id, _data=None, **kwds):
        node = self.element_class(self.client)
        node._update(_id, _data, kwds)
        return node

    def get_all(self):
        """Returns all the elements for the model type."""
        config = self.client.config
        type_var = config.type_var
        element_type = self.element_class.get_element_type(config)
        return self.index.lookup(type_var,element_type)

    def get_property_keys(self):
        return self.element_class._properties.keys()

class RelationshipProxy(EdgeProxy):

    def create(self, outV, inV, _data=None, **kwds):
        relationship = self.element_class(self.client)
        relationship._create(outV, inV, _data, kwds)
        return relationship

    def update(self, _id, _data=None, **kwds):
        relationship = self.element_class(self.client)
        relationship._update(_id, _data, kwds)
        return relationship

    def get_all(self):
        """Returns all the relationships for the label."""
        # TODO: find a blueprints method that returns all edges for a given label
        # because you many not want to index edges
        config = self.client.config
        label_var = config.label_var
        label = self.element_class.get_label(config)
        return self.index.lookup(label_var,label)

    def get_property_keys(self):
        return self.element_class._properties.keys()
        
