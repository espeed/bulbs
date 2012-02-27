# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Bulbs supports plugabble type systems.

"""
# Python 3
import six
import sys
if sys.version > '3':
    long = int
    unicode = str

from .utils import to_timestamp, to_datetime


class TypeSystem(object):
    """Abstract base class for plugabble database type systems."""

    #: The backend client's content type.
    content_type = None

    #: Converter object used to convert Python values to database values.
    database = None

    #: Converter object used to covert database values to Python values.
    python = None


class Converter(object):
    """Abstract base class of conversion methods called by DataType classes."""

    def to_string(self,value):
        raise NotImplementedError

    def to_integer(self,value):
        raise NotImplementedError
    
    def to_long(self,value):
        raise NotImplementedError

    def to_float(self,value):
        raise NotImplementedError

    def to_list(self,value):
        raise NotImplementedError

    def to_dictionary(self,value):
        raise NotImplementedError

    def to_null(self,value):
        raise NotImplementedError


#
# The JSON Type System
#

class Database(Converter):
    """Converts Python values to database values."""

    # The JSON type system is just a simple pass through.

    def to_string(self,value):
        # Using unicode instead of str
        return unicode(value)

    def to_integer(self,value):
        return value
    
    def to_long(self,value):
        return value

    def to_float(self,value):
        return value

    def to_list(self,value):
        return value

    def to_dictionary(self,value):
        return value

    def to_datetime(self, value):
        if value is not None:
            return to_timestamp(value)

    def to_null(self,value):
        return value


class Python(Converter):
    """Converts database values to Python values."""

    # Conversion exceptions are now handled in Property.convert_to_python() 
    
    def to_string(self,value):
        # Converting everything to unicode in Python 2.x 
        return unicode(value)

    def to_integer(self,value):
        return int(value)

    def to_long(self,value):
        return long(value)

    def to_float(self,value):
        return float(value)              

    def to_list(self,value):
        return list(value)

    def to_dictionary(self,value):
        return dict(value)

    def to_null(self,value):
        return None

    def to_datetime(self, value):
        if value is not None:
            return to_datetime(value)


class JSONTypeSystem(TypeSystem):

    content_type = "application/json"

    database = Database()
    python = Python()
    











