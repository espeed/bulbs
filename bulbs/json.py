# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
The JSON Type System.

"""
# Python 3
import six
import sys
if sys.version > '3':
    long = int
    unicode = str

from bulbs.base import TypeSystem, Converter
from .utils import to_timestamp, to_datetime, to_datestamp, to_date, json


class DatabaseConverter(Converter):
    """
    Converts Python values to database values.

    .. note:: Python to JSON conversion is usually just a simple pass through.

    """
    def to_string(self, value):
        """
        Converts a Python byte string to a unicode string.
        
        :param value: Property value. 
        :type value: str or None

        :rtype: unicode or None

        :raises: ValueError

        """
        # NOTE: Using unicode instead of str
        if value is not None:
            return unicode(value)

    def to_integer(self, value):
        """
        Passes through a Python integer.

        :param value: Property value. 
        :type value: int or None

        :rtype: int or None

        """
        return value
    
    def to_long(self, value):
        """
        Passes through a Python long.

        :param value: Property value. 
        :type value: long or None

        :rtype: long or None

        """
        return value

    def to_bool(self, value):
        """
        Passes through a Python bool.

        :param value: Property value.
        :type value: bool or None

        :rtype: bool or None

        """
        return value

    def to_float(self, value):
        """
        Passes through a Python float.

        :param value: Property value. 
        :type value: float or None

        :rtype: float or None

        """
        return value

    def to_list(self, value):
        """
        Passes through a Python list.

        :param value: Property value. 
        :type value: list or None

        :rtype: list or None

        """
        return value

    def to_dictionary(self, value):
        """
        Passes through a Python dictionary.

        :param value: Property value. 
        :type value: dict or None

        :rtype: dict or None

        """
        return value

    def to_datetime(self, value):
        """
        Converts a Python datetime object to a timestamp integer.

        :param value: Property value. 
        :type value: datetime or None

        :rtype: int or None

        """
        if value is not None:
            return to_timestamp(value)

    def to_date(self, value):
        """
        Converts a Python date object to a timestamp integer.

        :param value: Property value. 
        :type value: date or None

        :rtype: int or None

        """
        if value is not None:
            return to_datestamp(value)

    def to_null(self, value):
        """
        Passes through a Python None.

        :param value: Property value. 
        :type value: None

        :rtype: None

        """
        return value

    def to_document(self, value):
        """
        Converts a Python object to a json string

        :param value: Property value.
        :type value: dict or list or None

        :rtype: unicode or None
        """
        if value is not None:
            return unicode(json.dumps(value))


class PythonConverter(Converter):
    """Converts database values to Python values."""

    # TODO: Why are we checking if value is not None?
    # This is supposed to be handled elsewhere.
    # Conversion exceptions are now handled in Property.convert_to_python() 
    
    def to_string(self, value):
        """
        Converts a JSON string to a Python unicode string.
        
        :param value: Property value. 
        :type value: str or None

        :rtype: unicode or None

        :raises: ValueError

        """
        if value is not None:
            return unicode(value)

    def to_integer(self, value):
        """
        Converts a JSON number to a Python integer.

        :param value: Property value. 
        :type value: int or None

        :rtype: int or None

        :raises: ValueError

        """
        if value is not None:
            return int(value)

    def to_long(self, value):
        """
        Converts a JSON number to a Python long.

        :param value: Property value. 
        :type value: long or None

        :rtype: long or None

        :raises: ValueError

        """
        if value is not None:
            return long(value)

    def to_float(self, value):
        """
        Converts a JSON number to a Python float.

        :param value: Property value. 
        :type value: float or None

        :rtype: float or None

        :raises: ValueError

        """
        if value is not None:
            return float(value)              

    def to_bool(self, value):
        """
        Converts a JSON boolean value to a Python bool.

        :param value: Property value.
        :type value: bool or None

        :rtype: bool or None

        :raises: ValueError

        """
        if value is not None:
            return bool(value)

    def to_list(self, value):
        """
        Converts a JSON list to a Python list.

        :param value: Property value. 
        :type value: list or None

        :rtype: list or None

        :raises: ValueError

        """
        if value is not None:
            return list(value)

    def to_dictionary(self, value):
        """
        Converts a JSON map to a Python dictionary.         

        :param value: Property value. 
        :type value: dict or unicode or None

        :rtype: dict or None

        :raises: ValueError

        """
        if value is None:
            return None

        if isinstance(value, unicode):
            return json.loads(value)

        return dict(value)

    def to_datetime(self, value):
        """
        Converts a JSON integer timestamp to a Python datetime object.

        :param value: Property value. 
        :type value: int or None

        :rtype: datetime or None

        :raises: ValueError

        """
        if value is not None:
            return to_datetime(value)
            
    def to_date(self, value):
        """
        Converts a JSON integer timestamp to a Python date object.

        :param value: Property value. 
        :type value: int or None

        :rtype: date or None

        :raises: ValueError

        """
        if value is not None:
            return to_date(value)

    def to_null(self, value):
        """
        Converts a JSON null to a Python None.

        :param value: Property value. 
        :type value: None

        :rtype: None

        :raises: ValueError

        """
        if value is not None:
            raise ValueError

        return None


class JSONTypeSystem(TypeSystem):
    """
    Converts database properties to and from their JSON representations.

    :cvar content_type: The backend client's content type.
    :cvar database: Converter object. Converts Python values to database values.
    :cvar python: Converter object. Converts database values to Python values.

    """
    content_type = "application/json"

    database = DatabaseConverter()
    python = PythonConverter()
    











