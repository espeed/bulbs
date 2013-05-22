# -*- coding: utf-8 -*-
# 
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Base classes for modeling domain objects that wrap vertices and edges.

"""
import six  # Python 3
import inspect
import types
from collections import Callable

from bulbs.property import Property
from bulbs.element import Element, Vertex, VertexProxy, Edge, EdgeProxy, \
    coerce_vertices, build_data
from bulbs.utils import initialize_element, get_logger


# Model Modes
NORMAL = 1
STRICT = 2

log = get_logger(__name__)


class ModelMeta(type):
    """Metaclass used to set database Property definitions on Models."""

    def __init__(cls, name, base, namespace):
        """Store Property instance definitions on the class as a dictionary.""" 

        # Get inherited Properties
        cls._properties = cls._get_initial_properties()
        
        # Add new Properties
        cls._register_properties(namespace)

    def _get_initial_properties(cls):
        """
        Get Properties defined in the parent and inherit them.

        :rtype: dict

        """
        try: 
            parent_properties = getattr(cls, '_properties')
            properties = parent_properties.copy() 
        except:
            # Set it to an empty dict if the Model doesn't have a parent Model. 
            properties = {}
        return properties
            
    def _register_properties(cls, namespace):
        """
        Loop through the class namespace looking for Property instances.

        :param namespace: Class namespace
        :type namespace: dict

        :rtype: None

        """

        # e.g. age = Integer()
        for key in namespace: # Python 3
            value = namespace[key]

            assert key not in cls._properties, \
                "Can't redefine Property '%s'" % key

            if isinstance(value, Property):
                property_instance = value  # for clarity
                cls._properties[key] = property_instance
                cls._set_property_name(key,property_instance)
                cls._initialize_property(key,property_instance)
                # not doing this b/c some Properties are calculated at savetime
                #delattr(cls, key) 
                            
    def _set_property_name(cls, key, property_instance):
        """
        Set Property name to attribute key unless explicitly set via kwd param.

        :param key: Class attribute key
        :type key: str

        :param property_instance: Property instance
        :type property_instance bulbs.property.Property

        :rtype None

        """
        if property_instance.name is None:
            property_instance.name = key

    def _initialize_property(cls, key, property_instance):
        """
        Set the Model class attribute based on the Property definition.

        :param key: Class attribute key
        :type key: str

        :param property_instance: Property instance
        :type property_instance bulbs.property.Property

        """
        if property_instance.fget:
            # TODO: make this configurable
            # this is a calculated property (should it persist?)
            # wrapped fset and fdel in str() to make the default None not 
            # error on getattr
            fget = getattr(cls, property_instance.fget)
            # TODO: implement fset and fdel (maybe)
            #fset = getattr(cls, str(property_instance.fset), None)
            #fdel = getattr(cls, str(property_instance.fdel), None)
            fset = None
            fdel = None
            property_value = property(fget, fset, fdel)
        else:
            property_value = None
        setattr(cls, key, property_value)


class Model(six.with_metaclass(ModelMeta, object)):  # Python 3
    """Abstract base class for Node and Relationship container classes."""
    

    #: The mode for saving attributes to the database. 
    #: If set to STRICT, only defined Properties are saved.
    #: If set to NORMAL, all attributes are saved. 
    #: Defaults to NORMAL. 
    __mode__ = NORMAL
    
    #: A dict containing the database Property instances.
    _properties = None
    

    def __setattr__(self, key, value):
        """
        Set model attributes, possibly coercing database Properties to the 
        defined types.

        :param key: Attribute key
        :type key: str

        :param value: Attribute value
        :type value: object
        
        :rtype: None

        """
        if key in self._properties:
            self._set_database_property(key, value)
        else:
            # If _mode = STRICT, set an instance var, which isn't saved to DB.
            # If _mode = NORMAL, store in self._data, which is saved to DB
            self._set_normal_attribute(key, value)

    def _set_database_property(self, key, value):
        """
        Set Property attributes after coercing them into the defined types.

        :param key: Attribute key
        :type key: str

        :param value: Attribute value
        :type value: object
        
        :rtype: None

        """
        # we want Model Properties to be set be set as actual attributes
        # because they can be real Python propertes or calculated values,
        # which are calcualted/set upon each save().
        # Don't set calculated (fget) properties; they're calculated at save.
        if not self._is_calculated_property(key):
            value = self._coerce_property_value(key, value)
            object.__setattr__(self, key, value)

    def _set_normal_attribute(self, key, value):
        """
        Set normal/non-database Property attributes, depending on the __mode__.

        :param key: Attribute key
        :type key: str

        :param value: Attribute value
        :type value: object
        
        :rtype: None

        """
        if self.__mode__ == STRICT:
            # Set as a Python attribute, which won't be saved to the database.
            object.__setattr__(self, key, value)
        else:
            # Store the attribute in self._data, which are saved to database.
            Element.__setattr__(self, key, value)        

    def _is_calculated_property(self, key):
        """
        Returns True if the Property is a cacluated property, i.e. has fget set.

        :param key: Attribute key
        :type key: str

        :rtype: bool

        """
        # TODO: fget works, but fset, fdel have not been tested
        property_instance = self._properties[key]
        return (property_instance.fget is not None)

    def _coerce_property_value(self, key, value):
        """
        Coerce database Property value into its defined type.

        :param key: Attribute key
        :type key: str

        :param value: Attribute value
        :type value: object
        
        :rtype: object

        """
        if value is not None:
            property_instance = self._properties[key]
            value = property_instance.coerce(key, value)
        return value

    def _set_property_defaults(self):
        """
        Set the default values for all the database Properties.

        :rtype: None

        """
        for key in self._properties:
            default_value = self._get_property_default(key)     
            setattr(self, key, default_value)
            
    def _get_property_default(self, key):
        """
        Coerce database Property value into its defined type.

        :param key: Attribute key
        :type key: str

        :rtype: object

        """
        # TODO: make this work for model methods?
        # The value entered could be a scalar or a function name
        # Should we defer the call until all properties are set, 
        # or only for calculated properties?
        property_instance = self._properties[key]
        default_value = property_instance.default
        if isinstance(default_value, Callable):
            default_value = default_value()
        return default_value

    def _set_keyword_attributes(self, _data, kwds):
        """
        Sets Python attributes using the _data and keywords passed in by user.

        :param _data: Data that was passed in via a dict.
        :type _data: dict

        :param kwds: Data that was passed in via name/value pairs.
        :type kwds: dict

        :rtype: None

        """
        # NOTE: keys may have been passed in that are not defined as Properties
        data = build_data(_data, kwds)
        for key in data:    # Python 3
            value = data[key]  
            # Notice that __setattr__ is overloaded
            setattr(self, key, value)

    def _set_property_data(self):
        """
        Sets Property data after it is retrieved from the DB.

        :rtype: None

        .. note:: Sets the value to None if it's an invalid type.

        """
        type_system = self._client.type_system
        for key in self._properties:   # Python 3
            
            # Don't set calculted property values, i.e. those with fset defined.
            if self._is_calculated_property(key): continue

            property_instance = self._properties[key]
            #name = property_instance.name
            value = self._data.get(key, None)
            value = property_instance.convert_to_python(type_system, key, value)

            # TODO: Maybe need to wrap this in try/catch too.
            # Notice that __setattr__ is overloaded. No need to coerce it twice.
            object.__setattr__(self, key, value)
            
    def _get_property_data(self):
        """
        Returns validated Property data, ready to be saved in the DB.

        :rtype: dict

        """
        # If __mode__ is STRICT, data set to empty; otherwise set to self._data
        data = self._get_initial_data()

        type_var = self._client.config.type_var
        type_system = self._client.type_system

        if hasattr(self, type_var):
            # Add element_type to the database properties to be saved;
            # but don't worry about "label", it's always saved on the edge.
            data[type_var] = object.__getattribute__(self, type_var)

        # Convert database Property values to their database types.
        for key in self._properties:  # Python 3
            property_instance = self._properties[key]
            value = self._get_property_value(key)
            property_instance.validate(key, value)
            #name = property_instance.name
            db_value = property_instance.convert_to_db(type_system, key, value)
            data[key] = db_value

        return data

    def _get_initial_data(self):
        """
        Returns empty dict if __mode__ is set to STRICT, otherwise self._data.
        
        :rtype: dict

        """
        data = {} if self.__mode__ == STRICT else self._data.copy()
        return data

    def _get_property_value(self, key):
        """
        Returns the value of a Property, calculated via a function if needed.

        :param key: Attribute key
        :type key: str

        :rtype: object

        """
        # Notice that __getattr__ is overloaded in Element.
        value = object.__getattribute__(self, key)
        if isinstance(value, Callable):
            return value()
        return value

    def get_bundle(self, _data=None, **kwds):
        """
        Returns a tuple contaning the property data, index name, and index keys.

        :param _data: Data that was passed in via a dict.
        :type _data: dict

        :param kwds: Data that was passed in via name/value pairs.
        :type kwds: dict

        :rtype: tuple

        """
        self._set_property_defaults()   
        self._set_keyword_attributes(_data, kwds)
        data = self._get_property_data()
        index_name = self.get_index_name(self._client.config)
        keys = self.get_index_keys()
        return data, index_name, keys

    def get_index_keys(self):
        """
        Returns Property keys to index in DB. Defaults to None (index all keys).

        :rtype: list or None

        """
        # TODO: Derive this from Property definitions.
        return None

    def get_property_keys(self):
        """
        Returns a list of all the Property keys.

        :rtype: list

        """
        return self._properties.keys()

    def data(self):
        """
        Returns a the element's property data.

        :rtype: dict

        """
        data = dict()
        if self.__mode__ == NORMAL:
            data = self._data

        for key in self._properties: 
            # TODO: make this work for calculated values.
            # Calculated props shouldn't be stored, but components should be.
            data[key] = object.__getattribute__(self, key)
        return data

    def map(self):
        """
        Deprecated. Returns the element's property data.

        :rtype: dict

        """
        log.debug("This is deprecated; use data() instead.")
        return self.data()

    def __check__(self,data):
        """
        Override this method in the child class to throw an exception if the data dictionary is invalid
        
        :param data: Collection of parameters to be set for this Model
        :type data: dict

        """
        pass

class Node(Model, Vertex):
    """ 
    Abstract base class used for creating a Vertex Model.
 
    It's used to create classes that model domain objects, and it's not meant 
    to be used directly. To use it, create a subclass specific to the type of 
    data you are storing. 

    Example model declaration::

        # people.py

        from bulbs.model import Node
        from bulbs.property import String, Integer

        class Person(Node):
            element_type = "person"
            
            name = String(nullable=False)
            age = Integer()

    Example usage::

        >>> from people import Person
        >>> from bulbs.neo4jserver import Graph
        >>> g = Graph()

        # Add a "people" proxy to the Graph object for the Person model:
        >>> g.add_proxy("people", Person)

        # Use it to create a Person node, which also saves it in the database:
        >>> james = g.people.create(name="James")
        >>> james.eid
        3
        >>> james.name
        'James'

        # Get the node (again) from the database by its element ID:
        >>> james = g.people.get(james.eid)

        # Update the node and save it in the database:
        >>> james.age = 34
        >>> james.save()

        # Lookup people using the Person model's primary index:
        >>> nodes = g.people.index.lookup(name="James")
        
    """
    #: The mode for saving attributes to the database. 
    #: If set to STRICT, only defined Properties are saved.
    #: If set to NORMAL, all attributes are saved. 
    #: Defaults to NORMAL. 
    __mode__ = NORMAL
    
    #: A dict containing the database Property instances.
    _properties = None

    element_type = None

    @classmethod
    def get_element_type(cls, config):
        """
        Returns the element type.

        :param config: Config object.
        :type config: bulbs.config.Config

        :rtype: str

        """
        element_type = getattr(cls, config.type_var)
        return element_type

    @classmethod
    def get_element_key(cls, config):
        """
        Returns the element key.

        :param config: Config object.
        :type config: bulbs.config.Config

        :rtype: str

        """
        return cls.get_element_type(config)

    @classmethod 
    def get_index_name(cls, config):
        """
        Returns the index name. 

        :param config: Config object.
        :type config: bulbs.config.Config

        :rtype: str

        """
        return cls.get_element_type(config)

    @classmethod 
    def get_proxy_class(cls):
        """
        Returns the proxy class. 

        :param config: Config object.
        :type config: bulbs.config.Config

        :rtype: class

        """
        return NodeProxy


    def save(self):
        """
        Saves/updates the element's data in the database.

        :rtype: None

        """
        data = self._get_property_data()
        self.__check__(data)
        index_name = self.get_index_name(self._client.config)
        keys = self.get_index_keys()
        self._client.update_indexed_vertex(self._id, data, index_name, keys)
        
    #
    # Override the _create and _update methods to cusomize behavior.
    #
    
    def _create(self, _data, kwds):  
        """
        Creates a vertex in the database; called by the NodeProxy create() method.

        :param _data: Optional property data dict.
        :type _data: dict

        :param kwds: Optional property data keyword pairs. 
        :type kwds: dict

        :rtype: None
        
        """
        # bundle is an OrderedDict containing data, index_name, and keys
        data, index_name, keys = self.get_bundle(_data, **kwds)
        self.__check__(data)
        resp = self._client.create_indexed_vertex(data, index_name, keys)
        result = resp.one()
        self._initialize(result)
        
    def _update(self, _id, _data, kwds):
        """
        Updates a vertex in the database; called by NodeProxy update() method.
        
        :param _id: Element ID.
        :param _id: int or str

        :param _data: Optional property data dict.
        :type _data: dict

        :param kwds: Optional property data keyword pairs. 
        :type kwds: dict

        :rtype: None
        
        """
        data, index_name, keys = self.get_bundle(_data, **kwds)
        self.__check__(data)
        resp = self._client.update_indexed_vertex(_id, data, index_name, keys)
        result = resp.one()
        self._initialize(result)
        
    def _initialize(self, result):
        """
        Initializes the element. Initialize all non-DB attributes here.

        :param result: Result object.
        :type result: Result

        :rtype: None

        ..note:: Called by _create, _update, and utils.initialize_element. 

        """
        Vertex._initialize(self,result)
        self._initialized = False
        self._set_property_data()
        self._initialized = True


class Relationship(Model, Edge):
    """ 
    Abstract base class used for creating a Relationship Model.
 
    It's used to create classes that model domain objects, and it's not meant 
    to be used directly. To use it, create a subclass specific to the type of 
    data you are storing. 

    Example usage for an edge between a blog entry node and its creating user::

        # people.py

        from bulbs.model import Relationship
        from bulbs.properties import DateTime
        from bulbs.utils import current_timestamp

        class Knows(Relationship):

            label = "knows"

            created = DateTime(default=current_timestamp, nullable=False)


    Example usage::

          >>> from people import Person, Knows
          >>> from bulbs.neo4jserver import Graph
          >>> g = Graph()

          # Add proxy interfaces to the Graph object for each custom Model
          >>> g.add_proxy("people", Person)
          >>> g.add_proxy("knows", Knows)

          # Create two Person nodes, which are automatically saved in the DB
          >>> james = g.people.create(name="James")
          >>> julie = g.people.create(name="Julie")

          # Create a "knows" relationship between James and Julie:
          >>> knows = g.knows.create(james,julie)
          >>> knows.timestamp

          # Get the people James knows (the outgoing vertices labeled "knows")
          >>> friends = james.outV('knows')

    """
    label = None

    @classmethod
    def get_label(cls, config):
        """
        Returns the edge's label.

        :param config: Config object.
        :type config: bulbs.config.Config

        :rtype: str

        """
        label = getattr(cls, config.label_var)
        return label

    @classmethod
    def get_element_key(cls, config):
        """
        Returns the element key.

        :param config: Config object.
        :type config: bulbs.config.Config

        :rtype: str

        """
        return cls.get_label(config)

    @classmethod 
    def get_index_name(cls, config):
        """
        Returns the index name. 

        :param config: Config object.
        :type config: bulbs.config.Config

        :rtype: str

        """
        return cls.get_label(config)

    @classmethod 
    def get_proxy_class(cls):
        """
        Returns the proxy class. 

        :param config: Config object.
        :type config: bulbs.config.Config

        :rtype: class

        """
        return RelationshipProxy


    def save(self):
        """
        Saves/updates the element's data in the database.

        :rtype: None

        """
        data = self._get_property_data()
        self.__check__(data)

        index_name = self.get_index_name(self._client.config)
        keys = self.get_index_keys()
        self._client.update_indexed_edge(self._id, data, index_name, keys)

    #
    # Override the _create and _update methods to customize behavior.
    #

    def _create(self, outV, inV, _data, kwds):
        """
        Creates an edge in the DB; called by RelatinshipProxy create() method.

        :param _data: Optional property data dict.
        :type _data: dict

        :param kwds: Optional property data keyword pairs. 
        :type kwds: dict

        :rtype: None
        
        """
        label = self.get_label(self._client.config)
        outV, inV = coerce_vertices(outV, inV)
        data, index_name, keys = self.get_bundle(_data, **kwds)
        self.__check__(data)
        resp = self._client.create_indexed_edge(outV, label, inV, data, index_name, keys)
        result = resp.one()
        self._initialize(result)
        
    def _update(self, _id, _data, kwds):
        """
        Updates an edge in DB; called by RelationshipProxy update() method.
        
        :param _id: Element ID.
        :param _id: int or str

        :param _data: Optional property data dict.
        :type _data: dict

        :param kwds: Optional property data keyword pairs. 
        :type kwds: dict

        :rtype: None
        
        """
        data, index_name, keys = self.get_bundle(_data, **kwds)
        self.__check__(data)
        resp = self._client.update_indexed_edge(_id, data, index_name, keys)
        result = resp.one()
        self._initialize(result)

    def _initialize(self,result):
        """
        Initializes the element. Initialize all non-DB attributes here.

        :param result: Result object.
        :type result: Result

        :rtype: None

        ..note:: Called by _create, _update, and utils.initialize_element. 

        """
        Edge._initialize(self,result)
        self._initialized = False
        self._set_property_data()
        self._initialized = True


class NodeProxy(VertexProxy):

    def create(self, _data=None, **kwds):
        """
        Adds a vertex to the database and returns it.

        :param _data: Optional property data dict.
        :type _data: dict

        :param kwds: Optional property data keyword pairs. 
        :type kwds: dict

        :rtype: Node

        """
        node = self.element_class(self.client)
        node._create(_data, kwds)
        return node
        
    def update(self, _id, _data=None, **kwds):
        """
        Updates an element in the graph DB and returns it.

        :param _id: The vertex ID.
        :type _id: int or str

        :param _data: Optional property data dict.
        :type _data: dict

        :param kwds: Optional property data keyword pairs. 
        :type kwds: dict

        :rtype: Node

        """ 
        node = self.element_class(self.client)
        node._update(_id, _data, kwds)
        return node

    def get_all(self):
        """
        Returns all the elements for the model type.
        
        :rtype: Node generator
 
        """

        config = self.client.config
        type_var = config.type_var
        element_type = self.element_class.get_element_type(config)
        return self.index.lookup(type_var,element_type)

    def get_property_keys(self):
        """
        Returns a list of all the Property keys.

        :rtype: list

        """
        return self.element_class._properties.keys()

class RelationshipProxy(EdgeProxy):

    def create(self, outV, inV, _data=None, **kwds):
        """
        Creates an edge in the database and returns it.
        
        :param outV: The outgoing vertex. 
        :type outV: Vertex or int
              
        :param inV: The incoming vertex. 
        :type inV: Vertex or int

        :param _data: Optional property data dict.
        :type _data: dict

        :param kwds: Optional property data keyword pairs. 
        :type kwds: dict

        :rtype: Relationship

        """ 
        relationship = self.element_class(self.client)
        relationship._create(outV, inV, _data, kwds)
        return relationship

    def update(self, _id, _data=None, **kwds):
        """ 
        Updates an edge in the database and returns it. 
        
        :param _id: The edge ID.
        :type _id: int or str

        :param _data: Optional property data dict.
        :type _data: dict

        :param kwds: Optional property data keyword pairs. 
        :type kwds: dict

        :rtype: Relationship

        """
        relationship = self.element_class(self.client)
        relationship._update(_id, _data, kwds)
        return relationship

    def get_all(self):
        """
        Returns all the relationships for the label.

        :rtype: Relationship generator
 
        """
        # TODO: find a blueprints method that returns all edges for a given 
        # label because you many not want to index edges
        config = self.client.config
        label_var = config.label_var
        label = self.element_class.get_label(config)
        return self.index.lookup(label_var,label)


    def get_property_keys(self):
        """
        Returns a list of all the Property keys.

        :rtype: list

        """
        return self.element_class._properties.keys()
        
