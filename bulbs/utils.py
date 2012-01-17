# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
import os
import inspect

class LookupTable(object):

    def __init__(self):
        self.table = dict()
    
    def add(self,key,value):
        self.table[key] = value

    def get(self,key):
        return self.table[key]

def initialize_element(resource,result):
    # result should be a single Result object, not a list or generator
    element_class = get_element_class(resource,result)
    element = element_class(resource)
    element._initialize(result)
    return element

def initialize_elements(resource,response):
    # return None if there were no results; otherwise,
    # return a generator of initialized elements.
    if response.total_size > 0:
        for result in response.results:
            yield initialize_element(resource,result)

# TODO: this may be deprecated in favor of get_element_key
def get_element_type(resource,result):    
    element_type = result.data.get(resource.config.type_var,None)
    if not element_type:
        # just return the generic type for the Vertex/Edge class
        element_type = result.get_type()
    return element_type

def get_element_key(resource,result):
    var_map = dict(vertex=resource.config.type_var,
                   edge=resource.config.label_var)
    base_type = result.get_type()
    key_var = var_map[base_type]
    element_key = result.data.get(key_var,None)
    if not element_key:
        # just return the generic type for the Vertex/Edge class
        element_key = base_type
    return element_key

    
def get_element_class(resource,result):
    #element_type = get_element_type(resource,result)
    element_key = get_element_key(resource,result)
    element_class = resource.registry.get_class(element_key)
    return element_class

 
def get_one_result(resp):
    # If you're using this utility, that means the results attribute in the 
    # Response object should always contain a single result object,
    # not multiple items. But gremlin returns all results as a list
    # even if the list only contains one element, and the Response object
    # converts all lists to a generator of Result objects. Thus in that case,
    # we need to grab the single Result object out of the list/generator.
    if resp.total_size > 1:
        raise ValueError('resp.results contains more than one item.')
    if inspect.isgenerator(resp.results):
        result = resp.results.next()
    else:
        result = resp.results
    return result

def coerce_id(_id):
    # try to coerce the element ID string to an int.
    # ORIENTDB USES STRINGS SO THIS WON'T WORK FOR IT
    try:
        return int(_id)
    except:
        return _id

def quote(value):
    # quote it if it's a string, set to null if it's None, 
    # else return the value
    if type(value) == str:
        value = "'%s'" % value
    elif value is None:
        value = ""
    return value

def get_file_path(dir_name,file_name):
    return os.path.normpath(os.path.join(dir_name,file_name))

def build_path(*args):
    #path = "/".join(map(str,args))
    # don't include segment if it's None
    segments = [str(segment) for segment in args if segment]
    path = "/".join(segments)
    return path


