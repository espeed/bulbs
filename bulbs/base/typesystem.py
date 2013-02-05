# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Bulbs supports plugabble type systems.

"""

class TypeSystem(object):
    """
    Abstract base class for plugabble database type systems.

    :cvar content_type: The backend client's content type.
    :cvar database: Converter object. Converts Python values to database values.
    :cvar python: Converter object. Converts database values to Python values.

    """
    content_type = None
    database = None
    python = None


class Converter(object):
    """Abstract base class of conversion methods called by DataType classes."""

    def to_string(self, value):
        raise NotImplementedError

    def to_integer(self, value):
        raise NotImplementedError
    
    def to_long(self, value):
        raise NotImplementedError

    def to_float(self, value):
        raise NotImplementedError

    def to_bool(self, value):
        raise NotImplementedError

    def to_list(self, value):
        raise NotImplementedError

    def to_dictionary(self, value):
        raise NotImplementedError

    def to_null(self, value):
        raise NotImplementedError

    def to_document(self, value):
        raise NotImplementedError
