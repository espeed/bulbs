# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
import os
import inspect

#
# Element Utils
#

def initialize_elements(resource,response):
    # return None if there were no results; otherwise,
    # return a generator of initialized elements.
    if response.total_size > 0:
        for result in response.results:
            yield initialize_element(resource,result)

def initialize_element(resource,result):
    # result should be a single Result object, not a list or generator
    element_class = get_element_class(resource,result)
    element = element_class(resource)
    element._initialize(result)
    return element

def get_element_class(resource,result):
    element_key = get_element_key(resource,result)
    element_class = resource.registry.get_class(element_key)
    return element_class

def get_element_key(resource,result):
    var_map = dict(vertex=resource.config.type_var,
                   edge=resource.config.label_var)
    base_type = result.get_type()
    key_var = var_map[base_type]
    # if key_var not found, just return the generic type for the Vertex/Edge class
    element_key = result.data.get(key_var,base_type)
    return element_key
 
def get_one_result(resp):
    # If you're using this utility, that means the results attribute in the 
    # Response object should always contain a single result object,
    # not multiple items. But gremlin returns all results as a list
    # even if the list contains only one element. And the Response class
    # converts all lists to a generator of Result objects. Thus in that case,
    # we need to grab the single Result object out of the list/generator.
    if resp.total_size > 1:
        raise ValueError('resp.results contains more than one item.')
    if inspect.isgenerator(resp.results):
        result = resp.results.next()
    else:
        result = resp.results
    return result

#
# Resource Utils
#

def build_path(*args):
    #path = "/".join(map(str,args))
    # don't include segment if it's None
    segments = [str(segment) for segment in args if segment]
    path = "/".join(segments)
    return path

def get_file_path(dir_name,file_name):
    return os.path.normpath(os.path.join(dir_name,file_name))



