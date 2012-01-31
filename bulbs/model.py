# -*- coding: utf-8 -*-
# 
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Base classes for modeling domain objects that wrap vertices and edges.

"""
from bulbs.property import Property
from bulbs.element import Element, Vertex, VertexProxy, Edge, EdgeProxy
from bulbs.utils import initialize_element, get_one_result, get_logger

log = get_logger(__name__)


# Util used by NodeProxy and RelationshipProxy

def instantiate_model(element_class,resource,kwds):
    model = element_class(resource)
    model._set_keyword_attributes(kwds)
    return model


class ModelMeta(type):
    """Metaclass used to set database Property definitions on Models"""

    def __init__(cls, name, base, namespace):
        # store the Property definitions on the class as a dictionary 
        # mapping the Property key to the Property instance
        cls._properties = cls._get_initial_properties()
        cls._register_properties(namespace)

    def _get_initial_properties(cls):
        if not hasattr(cls, '_properties'):
            # Model doesn't have any registered properties
            properties = {}
        else:
            # Inherit properties and add more
            properties = cls._properties.copy()
        return properties
            

    def _register_properties(cls,namespace):
        # loop through the class namespace looking for database Property instances
        # e.g. age = Integer(), key: age, property_instance: Integer()
        for key, value in namespace.items():
            assert key not in cls._properties, "Can't redefine property '%s'" % key
            if isinstance(value, Property):
                property_instance = value  # for clarity
                cls._properties[key] = property_instance
                cls._set_property_name(key,property_instance)
                cls._set_property_default(key,property_instance)
                # not doing this b/c some Properties are calculated
                #delattr(cls, key) 
                
    def _set_property_name(cls,key,property_instance):
        # Property name will be none unless explicitly set via kwd param
        if property_instance.name is None:
            property_instance.name = key
            
    def _set_property_default(cls,key,property_instance):
        if property_instance.default is not None:
            # TODO: Make this work for scalars too -- huh?
            fget = getattr(cls,property_instance.default)
            # Or more to the point, why is this a Python property?
            default_value = property(fget)
        elif property_instance.fget:
            # wrapped fset and fdel in str() to make the default None work with getattr
            fget = getattr(cls,property_instance.fget)
            fset = getattr(cls,str(property_instance.fset),None)
            fdel = getattr(cls,str(property_instance.fdel),None)
            default_value = property(fget,fset,fdel)
        else:
            default_value = None
        setattr(cls,key,default_value)


class Model(object):

    __metaclass__ = ModelMeta

    strict = False

    def __setattr__(self, key, value):
        if key in self._properties:
            # we want Model properties to be set be set as actual attributes
            # because they can be real Python propertes or calculated values,
            # which are calcualted/set upon each save().
            value = self._coerce_property_value(key,value)
            object.__setattr__(self, key, value)
        else:
            Element.__setattr__(self, key, value)

    def _coerce_property_value(self,key,value):
        if value is not None:
            property_instance = self._properties[key]
            value = property_instance.coerce(key,value)
        return value

    def _set_keyword_attributes(self,kwds):
        for key, value in kwds.iteritems():
            # Notice that __setattr__ is overloaded
            setattr(self,key,value)

    def _set_property_data(self,result):
        """
        Sets Property data when an element is being initialized, after it is
        retrieved from the DB -- we set it to None if it won't set.        
        """
        type_system = self._resource.type_system
        for key, property_instance in self._properties.items():
            value = result.data.get(key,None)
            value = property_instance.convert_to_python(type_system,value)
            # Notice that __setattr__ is overloaded so bypassing it
            object.__setattr__(self, key, value)
        
    def _get_property_data(self):
        """Returns validated Property data, ready to be saved in the DB."""
        data = self._get_initial_data()
        type_var = self._resource.config.type_var
        type_system = self._resource.type_system
        if hasattr(self,type_var):
            # add element_type to the database properties to be saved;
            # but don't worry about "label", it's always saved on the edge
            data[type_var] = getattr(self,type_var)
        for key, property_instance in self._properties.items():
            value = getattr(self,key)
            property_instance.validate(key,value)
            value = property_instance.convert_to_db(type_system,value)
            data[key] = value
        return data

    def _get_initial_data(self):
        if self.strict:
            data = {}
        else:
            data = self._data.copy()
        return data

    def _get_index(self,index_name):
        try:
            index = self._resource.registry.get_index(index_name)
        except KeyError:
            index = None
        return index


class Node(Vertex,Model):


    def _initialize(self,result):
        # this is called by initialize_element; 
        # putting it here to ensure method resolution order
        # initialize all non-DB properties here
        Vertex._initialize(self,result)
        self._initialized = False
        self._set_property_data(result)
        element_type = self._get_element_type()
        self._index = self._get_index(element_type)
        self._initialized = True

    def _get_element_type(self):
        element_type = getattr(self,self._resource.config.type_var)
        return element_type

    def save(self):
        """Saves/updates the element's data in the database."""
        data = self._get_property_data()
        resp = self._update(self._id,data,self._index)
        # does _initialize really need to be called here?
        # maybe called Vertex._initialize directly b/c Neo4j doesn't return data
        #self._initialize(resp.results)
        return resp

    #
    # Override the _create and _update methods to cusomize behavior.
    #

    def _create(self,data,index):
        return self._resource.create_indexed_vertex(data,index.index_name)

    def _update(self,_id,data,index):
        return self._resource.update_indexed_vertex(_id,data,index.index_name)

        
class Relationship(Edge,Model):

    def _initialize(self,result):
        # this is called by initialize_element; 
        # putting it here to ensure method resolution order
        # initialize all non-DB properties here
        Edge._initialize(self,result)
        self._initialized = False
        self._set_property_data(result)
        label = self._get_label()
        self._index = self._get_index(label)
        self._initialized = True

    def _get_label(self):
        label = getattr(self,self._resource.config.label_var)
        return label

    def save(self):
        """Saves/updates the element's data in the database."""
        data = self._get_property_data()      
        resp = self._update(self._id,data)
        #self._initialize(resp.results)
        return resp

    #
    # Override the _create and _update methods to customize behavior.
    #

    def _create(self,outV,label,inV,data):
        return self._resource.create_edge(outV,label,inV,data)
        
    def _update(self,_id,data):
        return self._resource.update_edge(_id,data)


class NodeProxy(VertexProxy):

    def create(self,*args,**kwds):
        node = instantiate_model(self.element_class,self.resource,kwds)
        data = node._get_property_data()
        resp = node._create(data,self.index)
        result = get_one_result(resp)  
        # doing it this way you're losing any extra kwds that may have been set
        return initialize_element(self.resource,result)
        
    def update(self,_id,*args,**kwds):
        node = instantiate_model(self.element_class,self.resource,kwds)
        data = node._get_property_data()
        resp = node._update(_id,data,self.index)
        result = get_one_result(resp)
        return initialize_element(self.resource,result)

    def get_all(self):
        """Returns all the elements for the model type."""
        type_var = self.resource.config.type_var
        element_type = getattr(self.element_class,type_var)
        return self.index.get(type_var,element_type)


class RelationshipProxy(EdgeProxy):

    def create(self,*args,**kwds):
        relationship = instantiate_model(self.element_class,self.resource,kwds)
        outV, label, inV = self._parse_args(relationship,args)
        data = relationship._get_property_data()
        resp = relationship._create(outV,label,inV,data)
        result = get_one_result(resp)
        return initialize_element(self.resource,result)

    def update(self,_id,*args,**kwds):
        relationship = instantiate_model(self.element_class,self.resource,kwds)
        data = relationship._get_property_data()
        resp = relationship._update(_id,data)
        result = get_one_result(resp)
        return initialize_element(self.resource,result)

    def get_all(self):
        """Returns all the relationships for the label."""
        label_var = self.resource.config.label_var
        label = getattr(self.element_class,label_var)
        return self.index.get(label_var,label)

    def _parse_args(self,relationship,args):
        # Two different args options:
        # 1. generic relationship args: (outV, label, inV)
        # 2. subclassed relationship args: (outV, inV) 
        args = list(args)
        if args and isinstance(args[1],Vertex):
            # no label, so this is the subclassed format;
            # the label is defined on the relationship class
            outV = args.pop(0)
            inV = args.pop(0) 
            outV = self._coerce_vertex_id(outV)
            inV = self._coerce_vertex_id(inV)
            label = relationship._get_label()
            args = (outV,label,inV)
        return args


    
