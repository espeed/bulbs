# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#

import config
from property import Property, convert_to_rexster, convert_to_python

TYPE_VAR = config.TYPE_VAR

# NOTE: Here the word "Property" in ClassProperty refers to a Python property (lowercase)
# We are creating a custom class b/c the standard version won't work for classmethods 
class ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

class TypeSystemMeta(type):

    def __init__(cls, name, base, namespace):
        # store the Property definitions on the class as a dictionary
        # mapping the Property name to the Property instance
        cls._properties = {}

        # loop through the class namespace looking for Property instances
        for key, value in namespace.items():
            #print key,value
            if isinstance(value, Property):
                if value.name is None:
                    # name will be none unless set via kwd param
                    value.name = key
                cls._properties[key] = value
                # now that the property reference is stored away, 
                # initialize its vars to None, the default vale (TODO), or the fget
                if value.default:
                    #TODO: Make this work for scalars too
                    fget = getattr(cls,value.default)
                    value = property(fget)
                elif value.fget:
                    # wrapped fset and fdel in str() to make the default None work with getattr
                    fget = getattr(cls,value.fget)
                    fset = getattr(cls,str(value.fset),None)
                    fdel = getattr(cls,str(value.fdel),None)
                    value = property(fget,fset,fdel)
                else:
                    value = None
                setattr(cls,key,value)

class TypeSystem(object):

    __metaclass__ = TypeSystemMeta

    def _set_property(self,key,value):
        if key in self._properties:
            datatype = type(value)
            try:
                if value:
                    python_type = self._properties[key].datatype.python_type
                    # TODO: this is a HACK until we clean up 'None' values in DB
                    if value == 'None':
                        value = None
                    value = python_type(value)

                #if not self._properties[key].is_valid(value):
                #    raise TypeError('Invalid datatype for property.')  
                    #if value:
                        # some types can't be None
                    super(TypeSystem, self).__setattr__(key, value)
            except ValueError:
                print "'%s' is not a valid value for %s, must be  %s." \
                           % (value, key, python_type)
                raise
            except AttributeError:
                print "Can't set attribute '%s' to value '%s with type'" % (key,value,datatype)
                raise
        else:
            # set value normally (it's not a database "Property")
            # But don't try to set values for get-only attributes, such as eid
            #if type(self).__dict__[key].fset is not None:
            #try:
                # TODO: make this handle properties without fset 
            super(TypeSystem, self).__setattr__(key, value)
            #except:
            #    pass

    def __setattr__(self, key, value):
        self._set_property(key,value)

    def _constructor(self, kwds):
        """A simple constructor that allows initialization from kwargs.
        
        Sets attributes on the constructed instance using the names and
        values in ``kwargs``.
        
        Only keys that are present as
        attributes of the instance's class are allowed. These could be,
        for example, any mapped columns or relationships.
        """
        cls = type(self)
        for k in kwds:
            if not hasattr(cls,k):
                raise TypeError(
                    "%r is an invalid keyword argument for %s" %
                    (k, cls.__name__))
            setattr(self, k, kwds[k])



    def _set_property_data(self,results):
        """
        Sets Property data when an element is being initialized, after it is
        retrieved from the DB.

        This will do type checking and coerce values to the right datatype.
        
        """
        
        for key, property_instance in self._properties.items():
            value = results.get(key,None)
            #if property_instance.method is None:
                # this is a normal attribute, not a derived one so set its value
            try:
                setattr(self,key,value)
            except:
                # TODO: log/warn/email regarding type mismatch
                setattr(self,key,None)

    def _get_property_data(self):
        """Returns Property data ready to be saved in the DB."""
        data = dict()
        # it should default to string in rexster so no need to 
        # convert_to_rexster()
        # should we require element_type on nodes (i.e. Model vertices)?
        if hasattr(self,TYPE_VAR):
            data[TYPE_VAR] = getattr(self,TYPE_VAR)
        for key, value in self._properties.items():
            #try:
            val = getattr(self,key)
            #if isinstance(val,Property):
            #    data[key] = None
            #else:
            data[key] = convert_to_rexster(val)
                #data[key] = val
            #except:
            #    data[key] = None
        return data

    def _validate_property_data(self):
        """
        Validates that Property data is of the right datatype before saving it
        to the DB and that the Property has a value if nullable is set to False.
        
        Call this at the top of each save() method.
        
        """
        # check that Properties with nullable is set to False 
        # actually have a value set
        for key, property_instance in self._properties.items():
            if property_instance.nullable is False:
                try: 
                    assert getattr(self,key) is not None
                except AssertionError:
                    print "Cannot set '%s' to %s: '%s' is a Property with nullable set to False" % (key, getattr(self,key), key)
                    raise

    def _set_keyword_attributes(self,kwds):
        for key, value in kwds.iteritems():
            setattr(self,key,value)

