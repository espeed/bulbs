# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Interface for interacting with a graph database through Rexster.

"""

import logging
log = logging.getLogger(__name__)

# NOTE: "Property" refers to a graph-database property (i.e. the DB data)
class Property(object):

    def __init__(self, name=None, fget=None, fset=None, fdel=None, \
                     default=None, onupdate=None, constraint=None, \
                     nullable=True, unique=False, index=False):

        #self.datatype = datatype
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        # NOTE: If you pass name as a kwd, then it overwrites variables named "name"
        # FIX THIS!!!! -- why are they sharing the same namespace???
        self.name = name
        self.default = default
        self.nullable = nullable

        # These aren't implemented yet.         
        # TODO: unique creates an index
        self.index = index
        self.unique = unique
        self.onupdate = onupdate
        self.constraint = constraint


    def validate(self, key, value):
        """
        Validates that Property data is of the right datatype before saving it
        to the DB and that the Property has a value if nullable is set to False.
        
        """
        self._check_datatype(value)
        self._check_null(key,value)

    def _check_datatype(self,value):
        isinstance(value, self.python_type)

    def _check_null(self,key,value):
        try: 
            if self.nullable is False:
                # should this be "assert value is True" to catch empties?
                assert value is not None
        except AssertionError:
           log.error("Null Property Error: '%s' cannot be set to '%s'", \
                         key, value)
           raise

    # TODO: Simplify these, and make method names consistent....
    def coerce_from_db_to_python(self,type_system,value):
        try:
            value = self.to_python(type_system,value)
        except Exception as e:
            # TODO: log/warn/email regarding type mismatch
            log.error("Property Type Mismatch: '%s' with value '%s': %s", key, value, ex)
            value = None
        return value

    def coerce_from_python_to_db(self,type_system,value):
        value = self.to_db(type_system,value)
        return value

    def coerce_from_python_to_python(self,key,value):
        initial_datatype = type(value)
        try:
            value = self.python_type(value)
            return value
        except ValueError:
            print "'%s' is not a valid value for %s, must be  %s." \
                           % (value, key, self.python_type)
            raise
        except AttributeError:
            print "Can't set attribute '%s' to value '%s with type %s'" \
                % (key,value,initial_datatype)
            raise


class String(Property): 

    python_type = str

    def to_db(self,type_system,value):
        return type_system.database.to_string(value)

    def to_python(self,type_system,value):
        return type_system.python.to_string(value)    

class Integer(Property):    

    python_type = int

    def to_db(self,type_system,value):
        return type_system.database.to_integer(value)
    
    def to_python(self,type_system,value):
        return type_system.python.to_integer(value)

class Long(Property):

    python_type = long

    def to_db(self,type_system,value):
        return type_system.database.to_long(value)

    def to_python(self,type_system,value):
        return type_system.python.to_long(value)

class Float(Property):

    python_type = float

    def to_db(self,type_system,value):
        return type_system.database.to_float(value)
    
    def to_python(self,type_system,value):
        return type_system.python.to_float(value)              

class Null(Property):

    python_type = None

    def to_db(self,type_system,value):
        return type_system.database.to_null(value)

    def to_python(self,type_system,value):
        return type_system.python.to_null(value)

class List(Property):

    python_type = list

    def to_db(self,type_system,value):
        return type_system.database.to_list(value)

    def to_python(self,type_system,value):
        return type_system.python.to_list(value)

class Dictionary(Property):

    python_type = dict

    def to_db(self,type_system,value):
        return type_system.database.to_dictionary(value)

    def to_python(self,type_system,value):
        return type_system.python.to_dictionary(value)

