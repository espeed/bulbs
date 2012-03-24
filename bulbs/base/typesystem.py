# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Bulbs supports plugabble type systems.

"""

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
