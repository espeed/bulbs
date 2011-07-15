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


def convert_to_python(data):
    datatype = data['type']
    value = data['value']
    klass = type_map[datatype]
    return klass.to_python(value)

def convert_to_rexster(data):
    datatype = type(data)
    value = data
    klass = type_map[datatype]
    return klass.to_rexster(value)


# NOTE 1: "Property" refers to a graph-database property (i.e. the DB data)
class Property(object):

    def __init__(self, datatype, fget=None, fset=None, fdel=None, \
                     name=None, default=None, onupdate=None, constraint=None, \
                     nullable=True, unique=False, index=False):

        # TODO: unique creates an index

        #args = list(args)
        #name = args.pop(0)
        #proptype = args.pop(0)

        #self.nullable = kwargs.pop('nullable', not self.primary_key)
        #self.default = kwargs.pop('default', None)
        #self.index = kwargs.pop('index', None)
        #self.unique = kwargs.pop('unique', None)
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

    def is_valid(self, value):
        return isinstance(value, self.datatype.python_type)


class DataType(object):

    def __init__(self):
        # TODO: Is this being used or 
        # are you explicitly setting them at bottom of this module?
        type_map.update(self.python_type,self.__class__)
        type_map.update(self.rexter_type,self.__class__)

    @classmethod
    def convert(self,value,datatype):
        # TODO: warn or log errors
        try: return datatype(value)
        except: return None


class String(DataType): 
    python_type = str
    rexster_type = "string"

    @classmethod
    def to_rexster(self,value):
        return '(string,%s)' % (value)
    
    @classmethod
    def to_python(self,value):
        return self.convert(value,str)

class Integer(DataType):    
    python_type = int
    rexter_type = "integer"
    
    @classmethod
    def to_rexster(self,value):
        return '(integer,%d)' % (value)
    
    @classmethod
    def to_python(self,value):
        return self.convert(value,int)

class Long(DataType):
    python_type = long
    rexster_type = "long"
    
    @classmethod
    def to_rexster(self,value):
        return '(long,%d)' % (value)

    @classmethod
    def to_python(self,value):
        return self.convert(value,long)

class Float(DataType):
    python_type = float
    rexter_type = "float"
    
    @classmethod
    def to_rexster(self,value):
        return '(float,%f)' % (value)
    
    @classmethod
    def to_python(self,value):
        return self.convert(value,float)              

class Null(DataType):
    python_type = None
    rexter_type = "string"

    @classmethod
    def to_rexster(self,value):
        # TODO: we prob don't want to save None values as 
        # empty strings in Rexter, instead just ignore them
        return '(string,%s)' % ('')
    
    @classmethod
    def to_python(self,value):
        return None

class List(DataType):
    python_type = list
    rexster_type = "list"

    @classmethod
    def to_rexster(self,value):
        val_list = []
        for item in value:
            val_list.append(convert_to_rexster(item))
        return "(list,(%s))" % (','.join(val_list))    

    @classmethod
    def to_python(self,value):
        val_list = []
        for item in value:
            val_list.append(convert_to_python(item))
        return val_list

class Dictionary(DataType):
    python_type = dict
    rexster_type = "map"

    @classmethod
    def to_rexster(self,value):
        pair_list = []
        for k,v in value.items():
            pair = "%s=%s" % (k,convert_to_rexster(v))
            pair_list.append(pair)
        return "(map,(%s))" % (','.join(pair_list))    

    @classmethod
    def to_python(self,value):
        dict_ = {}
        for k,v in value.items():
            dict_.update({k:convert_to_python(v)})
        return dict_

type_map = dict()
type_map[str] = String
type_map['string'] = String
type_map[int] = Integer
type_map['integer'] = Integer
type_map[float] = Float
type_map['float'] = Float
type_map[list] = List
type_map['list'] = List
type_map[dict] = Dictionary
type_map['map'] = Dictionary
type_map['array'] = List
type_map[type(None)] = Null
