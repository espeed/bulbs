# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Interface for interacting with a graph database through Rexster.

Graph, Vertex, Edge, Index, Query

"""
#import array


# NOTE 1: "Property" refers to a graph-database property (i.e. the DB data)
class Property(object):

    def __init__(self, datatype, fget=None, fset=None, fdel=None, \
                     name=None, default=None, onupdate=None, constraint=None, \
                     nullable=True, unique=False, index=False):

        # TODO: unique creates an index
        self.datatype = datatype
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        # NOTE: If you pass name as a kwd, then it overwrites variables named "name"
        # FIX THIS!!!! -- why are they sharing the same namespace???
        self.name = name
        self.default = default
        self.onupdate = onupdate
        self.constraint = constraint,
        self.nullable = nullable
        self.unique = unique
        self.index = index

    def _check_datatype(self,value):
        isinstance(value, self.datatype.python_type)

    def _check_null(self,key,value):
        try: 
            if self.nullable is False:
                # should this be "assert value is True" to catch empties?
                assert value is not None
        except AssertionError:
            print "Cannot set '%s' to %s: '%s' is a Property with nullable set to False" \
                % (key, value, key)
            raise

    def validate(self, key, value):
        """
        Validates that Property data is of the right datatype before saving it
        to the DB and that the Property has a value if nullable is set to False.
        
        Call this at the top of each save() method.
        
        """
        self._check_datatype(value)
        self._check_null(key,value)

    def coerce_value(self,key,value):
        initial_datatype = type(value)
        try:
            python_type = self.datatype.python_type
            value = python_type(value)
            return value
        except ValueError:
            print "'%s' is not a valid value for %s, must be  %s." \
                           % (value, key, python_type)
            raise
        except AttributeError:
            print "Can't set attribute '%s' to value '%s with type %s'" \
                % (key,value,initial_datatype)
            raise


class DataType(object):
    pass

class String(DataType): 

    python_type = str

    @classmethod
    def to_db(self,type_system,value):
        return type_system.string_to_db(value)

    @classmethod
    def to_python(self,type_system,value):
        return type_system.convert(value,str)

class Integer(DataType):    

    python_type = int

    @classmethod
    def to_db(self,type_system,value):
        return type_system.integer_to_db(value)
    
    @classmethod
    def to_python(self,type_system,value):
        return type_system.convert(value,int)

class Long(DataType):

    python_type = long

    @classmethod
    def to_db(self,type_system,value):
        return type_system.long_to_db(value)

    @classmethod
    def to_python(self,type_system,value):
        return type_system.convert(value,long)

class Float(DataType):

    python_type = float

    @classmethod
    def to_db(self,type_system,value):
        return type_system.float_to_db(value)
    
    @classmethod
    def to_python(self,type_system,value):
        return type_system.convert(value,float)              

class Null(DataType):

    python_type = None

    @classmethod
    def to_db(self,type_system,value):
        return type_system.null_to_db(value)

    @classmethod
    def to_python(self,type_system,value):
        type_system.null_to_python(value)

class List(DataType):

    python_type = list

    @classmethod
    def to_db(self,type_system,value):
        return type_system.list_to_db(value)

    @classmethod
    def to_python(self,type_system,value):
        type_system.list_to_python(value)

class Dictionary(DataType):

    python_type = dict

    @classmethod
    def to_db(self,type_system,value):
        return type_system.dictionary_to_db(value)

    @classmethod
    def to_python(self,type_system,value):
        type_system.dictionary_to_python(value)

