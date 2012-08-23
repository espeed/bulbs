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
    """
    Abstract base class for database property types used in Models.

    :param fget: Method name that returns a calculated value. Defaults to None.
    :type fget: str

    :param name: Database property name. Defaults to the Property key.
    :type name: str

    :param default: Default property value. Defaults to None.
    :type default: str, int, long, float, list, dict, or Callable

    :param nullable: If True, the Property can be null. Defaults to True.
    :type nullable: bool

    :param indexed: If True, index the Property in the DB. Defaults to False.
    :type indexeded: bool

    :ivar fget: Name of the method that gets the calculated Property value.
    :ivar name: Database property name. Defaults to the Property key.
    :ivar default: Default property value. Defaults to None.
    :ivar nullable: If True, the Property can be null. Defaults to True.
    :ivar indexed: If True, index the Property in the DB. Defaults to False.

    .. note:: If no Properties have index=True, all Properties are indexed. 

    """
    def __init__(self, fget=None, name=None, default=None, \
                     nullable=True, unique=False, indexed=False):
        self.fget = fget
        self.name = name
        self.default = default
        self.nullable = nullable

        # These aren't implemented yet.         
        # TODO: unique creates an index
        self.indexed = indexed
        self.unique = unique
        #self.constraint = constraint


    def validate(self, key, value):
        """
        Validates the Property value before saving it to the database.
        
        :param key: Property key.
        :type key: str

        :param value: Property value.
        :type value: object

        :rtype: None

        """
        # Do null checks first so you can ignore None values in check_datatype()
        self._check_null(key, value)
        self._check_datatype(key, value)

    def _check_null(self,key,value):
        # TODO: should this be checking that the value is True to catch empties?
        if self.nullable is False and value is None:
            log.error("Null Property Error: '%s' cannot be set to '%s'", 
                      key, value)
            raise ValueError

    def _check_datatype(self, key, value):
        if value is not None and isinstance(value, self.python_type) is False:
            log.error("Type Error: '%s' is set to %s with type %s, but must be a %s.", 
                      key, value, type(value), self.python_type)
            raise TypeError

    def convert_to_db(self, type_system, key, value):
        """
        Converts a Property value from its Python type to its database representation.

        :param type_system: TypeSystem object.
        :type type_system: TypeSystem

        :param key: Property key.
        :type key: str

        :param value: Property value.
        :type value: object

        :rtype: object

        """
        value = self.to_db(type_system,value)
        return value

    def convert_to_python(self, type_system, key, value):
        """
        Converts a Property value from its database representation to its Python type.

        :param type_system: TypeSystem object.
        :type type_system: TypeSystem

        :param key: Property key.
        :type key: str

        :param value: Property value.
        :type value: object

        :rtype: object

        """
        try:
            value = self.to_python(type_system, value)
        except Exception as e:
            log.exception("Property Type Mismatch: '%s' with value '%s': %s", 
                          key, value, e)
            value = None
        return value

    def coerce(self, key, value):
        """
        Coerces a Property value to its Python type.
        
        :param key: Property key.
        :type key: str
        
        :param value: Property value.
        :type value: object

        :rtype: object        

        """
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
    """
    :param fget: Method name that returns a calculated value. Defaults to None.
    :type fget: str
    
    :param name: Database property name. Defaults to the Property key.
    :type name: str

    :param default: Default property value. Defaults to None.
    :type default: str, int, long, float, list, dict, or Callable

    :param nullable: If True, the Property can be null. Defaults to True.
    :type nullable: bool

    :param indexed: If True, index the Property in the DB. Defaults to False.
    :type indexed: bool

    :ivar fget: Name of the method that gets the calculated Property value.
    :ivar name: Database property name. Defaults to the Property key.
    :ivar default: Default property value. Defaults to None.
    :ivar nullable: If True, the Property can be null. Defaults to True.
    :ivar indexed: If True, index the Property in the DB. Defaults to False.

    .. note:: If no Properties have index=True, all Properties are indexed. 

    """
    #: Python type
    python_type = unicode

    def to_db(self,type_system,value):
        return type_system.database.to_string(value)

    def to_python(self,type_system,value):
        return type_system.python.to_string(value)    

class Integer(Property):    
    """
    :param fget: Method name that returns a calculated value. Defaults to None.
    :type fget: str

    :param name: Database property name. Defaults to the Property key.
    :type name: str

    :param default: Default property value. Defaults to None.
    :type default: str, int, long, float, list, dict, or Callable

    :param nullable: If True, the Property can be null. Defaults to True.
    :type nullable: bool

    :param indexed: If True, index the Property in the DB. Defaults to False.
    :type indexed: bool

    :ivar fget: Name of the method that gets the calculated Property value.
    :ivar name: Database property name. Defaults to the Property key.
    :ivar default: Default property value. Defaults to None.
    :ivar nullable: If True, the Property can be null. Defaults to True.
    :ivar indexed: If True, index the Property in the DB. Defaults to False.

    .. note:: If no Properties have index=True, all Properties are indexed. 

    """
    #: Python type
    python_type = int

    def to_db(self,type_system,value):
        return type_system.database.to_integer(value)
    
    def to_python(self,type_system,value):
        return type_system.python.to_integer(value)

class Long(Property):
    """
    :param fget: Method name that returns a calculated value. Defaults to None.
    :type fget: str

    :param name: Database property name. Defaults to the Property key.
    :type name: str

    :param default: Default property value. Defaults to None.
    :type default: str, int, long, float, list, dict, or Callable

    :param nullable: If True, the Property can be null. Defaults to True.
    :type nullable: bool

    :param indexed: If True, index the Property in the DB. Defaults to False.
    :type indexed: bool

    :ivar fget: Name of the method that gets the calculated Property value.
    :ivar name: Database property name. Defaults to the Property key.
    :ivar default: Default property value. Defaults to None.
    :ivar nullable: If True, the Property can be null. Defaults to True.
    :ivar indexed: If True, index the Property in the DB. Defaults to False.

    .. note:: If no Properties have index=True, all Properties are indexed. 

    """
    #: Python type
    python_type = long

    def to_db(self,type_system,value):
        return type_system.database.to_long(value)

    def to_python(self,type_system,value):
        return type_system.python.to_long(value)

class Float(Property):
    """
    :param fget: Method name that returns a calculated value. Defaults to None.
    :type fget: str

    :param name: Database property name. Defaults to the Property key.
    :type name: str

    :param default: Default property value. Defaults to None.
    :type default: str, int, long, float, list, dict, or Callable

    :param nullable: If True, the Property can be null. Defaults to True.
    :type nullable: bool

    :param indexed: If True, index the Property in the DB. Defaults to False.
    :type indexed: bool

    :ivar fget: Name of the method that gets the calculated Property value.
    :ivar name: Database property name. Defaults to the Property key.
    :ivar default: Default property value. Defaults to None.
    :ivar nullable: If True, the Property can be null. Defaults to True.
    :ivar indexed: If True, index the Property in the DB. Defaults to False.

    .. note:: If no Properties have index=True, all Properties are indexed. 

    """
    #: Python type
    python_type = float

    def to_db(self,type_system,value):
        return type_system.database.to_float(value)
    
    def to_python(self,type_system,value):
        return type_system.python.to_float(value)              

class Null(Property):
    """
    :param fget: Method name that returns a calculated value. Defaults to None.
    :type fget: str
    
    :param name: Database property name. Defaults to the Property key.
    :type name: str

    :param default: Default property value. Defaults to None.
    :type default: str, int, long, float, list, dict, or Callable

    :param nullable: If True, the Property can be null. Defaults to True.
    :type nullable: bool

    :param indexed: If True, index the Property in the DB. Defaults to False.
    :type indexed: bool

    :ivar fget: Name of the method that gets the calculated Property value.
    :ivar name: Database property name. Defaults to the Property key.
    :ivar default: Default property value. Defaults to None.
    :ivar nullable: If True, the Property can be null. Defaults to True.
    :ivar indexed: If True, index the Property in the DB. Defaults to False.

    .. note:: If no Properties have index=True, all Properties are indexed. 

    """
    #: Python type
    python_type = None

    def to_db(self,type_system,value):
        return type_system.database.to_null(value)

    def to_python(self,type_system,value):
        return type_system.python.to_null(value)

class List(Property):
    """
    :param fget: Method name that returns a calculated value. Defaults to None.
    :type fget: str
    
    :param name: Database property name. Defaults to the Property key.
    :type name: str

    :param default: Default property value. Defaults to None.
    :type default: str, int, long, float, list, dict, or Callable

    :param nullable: If True, the Property can be null. Defaults to True.
    :type nullable: bool

    :param indexed: If True, index the Property in the DB. Defaults to False.
    :type indexed: bool

    :ivar fget: Name of the method that gets the calculated Property value.
    :ivar name: Database property name. Defaults to the Property key.
    :ivar default: Default property value. Defaults to None.
    :ivar nullable: If True, the Property can be null. Defaults to True.
    :ivar indexed: If True, index the Property in the DB. Defaults to False.

    .. note:: If no Properties have index=True, all Properties are indexed. 

    """
    #: Python type
    python_type = list

    def to_db(self,type_system,value):
        return type_system.database.to_list(value)

    def to_python(self,type_system,value):
        return type_system.python.to_list(value)

class Dictionary(Property):
    """
    :param fget: Method name that returns a calculated value. Defaults to None.
    :type fget: str
    
    :param name: Database property name. Defaults to the Property key.
    :type name: str

    :param default: Default property value. Defaults to None.
    :type default: str, int, long, float, list, dict, or Callable

    :param nullable: If True, the Property can be null. Defaults to True.
    :type nullable: bool

    :param indexed: If True, index the Property in the DB. Defaults to False.
    :type indexed: bool

    :ivar fget: Name of the method that gets the calculated Property value.
    :ivar name: Database property name. Defaults to the Property key.
    :ivar default: Default property value. Defaults to None.
    :ivar nullable: If True, the Property can be null. Defaults to True.
    :ivar indexed: If True, index the Property in the DB. Defaults to False.

    .. note:: If no Properties have index=True, all Properties are indexed. 

    """
    #: Python type
    python_type = dict

    def to_db(self,type_system,value):
        return type_system.database.to_dictionary(value)

    def to_python(self,type_system,value):
        return type_system.python.to_dictionary(value)


class Document(Property):
    """
    :param fget: Method name that returns a calculated value. Defaults to None.
    :type fget: str
    
    :param name: Database property name. Defaults to the Property key.
    :type name: str

    :param default: Default property value. Defaults to None.
    :type default: str, int, long, float, list, dict, or Callable

    :param nullable: If True, the Property can be null. Defaults to True.
    :type nullable: bool

    :param indexed: If True, index the Property in the DB. Defaults to False.
    :type indexed: bool

    :ivar fget: Name of the method that gets the calculated Property value.
    :ivar name: Database property name. Defaults to the Property key.
    :ivar default: Default property value. Defaults to None.
    :ivar nullable: If True, the Property can be null. Defaults to True.
    :ivar indexed: If True, index the Property in the DB. Defaults to False.

    .. note:: If no Properties have index=True, all Properties are indexed. 

    """
    #: Python type
    python_type = dict

    def to_db(self,type_system,value):
        return type_system.database.to_document(value)

    def to_python(self,type_system,value):
        return type_system.python.to_dictionary(value)


class DateTime(Property):
    """
    :param fget: Method name that returns a calculated value. Defaults to None.
    :type fget: str

    :param name: Database property name. Defaults to the Property key.
    :type name: str

    :param default: Default property value. Defaults to None.
    :type default: str, int, long, float, list, dict, or Callable

    :param nullable: If True, the Property can be null. Defaults to True.
    :type nullable: bool

    :param indexed: If True, index the Property in the DB. Defaults to False.
    :type indexed: bool

    :ivar fget: Name of the method that gets the calculated Property value.
    :ivar name: Database property name. Defaults to the Property key.
    :ivar default: Default property value. Defaults to None.
    :ivar nullable: If True, the Property can be null. Defaults to True.
    :ivar indexed: If True, index the Property in the DB. Defaults to False.

    .. note:: If no Properties have index=True, all Properties are indexed. 

    """
    #: Python type
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
        
        if isinstance(value, Number):
            # catches unix timestamps
            dt = to_datetime(value)
        elif isinstance(value, datetime.datetime):  
            # value passed in was already in proper form
            dt = value
        else:
            # Python 3 unicode/str catchall
            dt = dateutil.parser.parse(value)

        #if dt.tzinfo is None:
        #    tz = pytz.timezone('UTC')
        #    dt.replace(tzinfo = tz)

        return dt

    
