# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Interface for interacting with a graph database through Rexster.

"""
# Python 3
import six
import sys
if sys.version > '3':
    long = int
    unicode = str

import datetime
import dateutil.parser
from numbers import Number

from .utils import get_logger, to_datetime

log = get_logger(__name__)


class Property(object):
    """Container for a graph-database property used to create Models."""

    def __init__(self, name=None, fget=None, fset=None, fdel=None, \
                     default=None, onupdate=None, constraint=None, \
                     nullable=True, unique=False, index=False):

        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        # NOTE: If you pass name as a kwd, then it overwrites variables named "name"
        # FIX THIS!!!! -- why are they sharing the same namespace??? 
        # The above is an old comment -- is this still an issue?
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
        # Do null checks first so you can ignore None values in check_datatype
        self._check_null(key, value)
        self._check_datatype(key, value)


    def _check_datatype(self,key, value):
        if value is None:
            return
        if not isinstance(value, self.python_type):
            log.error("Type Error: '%s' is set to %s with type %s, but must be a %s.", 
                      key, value, type(value), self.python_type)
            raise TypeError

    def _check_null(self,key,value):
        try: 
            if self.nullable is False:
                # should this be "assert value is True" to catch empties?
                assert value is not None
        except AssertionError:
           log.error("Null Property Error: '%s' cannot be set to '%s'", 
                     key, value)
           raise ValueError

    def convert_to_db(self,type_system,value):
        value = self.to_db(type_system,value)
        return value

    def convert_to_python(self, type_system, key, value):
        try:
            value = self.to_python(type_system, value)
        except Exception as e:
            log.exception("Property Type Mismatch: '%s' with value '%s': %s", 
                          key, value, e)
            value = None
        return value

    def coerce(self,key,value):
        initial_datatype = type(value)
        try:
            value = self._coerce(value)
            return value
        except ValueError:
            log.exception("'%s' is not a valid value for %s, must be  %s.", 
                          value, key, self.python_type)
            raise
        except AttributeError:
            log.exception("Can't set attribute '%s' to value '%s with type %s'", 
                          key, value, initial_datatype)
            raise

    def _coerce(self, value):
        # overload coerce for special types like DateTime
        return self.python_type(value)

class String(Property): 

    python_type = unicode

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


class DateTime(Property):

    python_type = datetime.datetime

    def to_db(self, type_system, value):
        return type_system.database.to_datetime(value)

    def to_python(self, type_system, value):
        return type_system.python.to_datetime(value)

    def is_valid(self, key, value):
        # how do you assert it's UTC?
        #Don't use assert except for sanity check during development 
        # (it gets turned to a no-op when you run with python -o), and 
        # don't raise the wrong kind of exception (such as, an AssertionError 
        # when a TypeError is clearly what you mean here).
        #return type(value) is datetime.datetime
        return isinstance(value, datetime.datetime)

    def _coerce(self, value):
        # Coerce user input to the Python type
        # Overloaded from Property since this is a special case
        # http://labix.org/python-dateutil#head-a23e8ae0a661d77b89dfb3476f85b26f0b30349c
        # return dateutils.parse(value)
        # Not using parse -- let the client code do that. Expect a UTC dateime object here.
        # How you going to handle asserts? It's easy with ints.
        
        print type(value), value
        if isinstance(value, Number):
            # catches unix timestamps
            dt = to_datetime(value)
        elif not isinstance(value, datetime.datetime):  
            # Python 3 unicode/str catchall
            dt = dateutil.parser.parse(value)
        else:
            # value passed in was already in proper form
            dt = value

        #if dt.tzinfo is None:
        #    tz = pytz.timezone('UTC')
        #    dt.replace(tzinfo = tz)

        return dt

# have both?
# You don't need both, unless you're trying to eek out performance by saving on the conversion step

class Timestamp(Property):
    pass
    
