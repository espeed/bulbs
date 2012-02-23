# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
import os
import sys
import inspect
import logging


#
# Python 3 
#

if sys.version < '3':
    import codecs
    import ujson as json
    from urllib import quote
    from urllib import urlencode
    from urlparse import urlsplit

    def u(x):
        return codecs.unicode_escape_decode(x)[0]
else:
    # ujson is faster but hasn't been ported to Python 3 yet
    import json
    from urllib.parse import quote
    from urllib.parse import urlencode
    from urllib.parse import urlsplit

    def u(x):
        return x

#
# Logging
#

def get_logger(name,level=None):
    logger = logging.getLogger(name)
    if level:
        logger.setLevel(level)
    return logger

log = get_logger(__name__)

#
# Element Utils
#

def initialize_elements(client,response):
    # return None if there were no results; otherwise,
    # return a generator of initialized elements.
    if response.total_size > 0:
        for result in response.results:
            yield initialize_element(client,result)

def initialize_element(client,result):
    # result should be a single Result object, not a list or generator
    element_class = get_element_class(client,result)
    element = element_class(client)
    element._initialize(result)
    return element

def get_element_class(client,result):
    element_key = get_element_key(client,result)
    element_class = client.registry.get_class(element_key)
    return element_class

def get_element_key(client,result):
    var_map = dict(vertex=client.config.type_var,
                   edge=client.config.label_var)
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
        log.error('resp.results contains more than one item.')
        raise ValueError
    if inspect.isgenerator(resp.results):
        result = next(resp.results)
    else:
        result = resp.results
    return result
    


#
# Client Utils
#

def build_path(*args):
    #path = "/".join(map(str,args))
    # don't include segment if it's None
    segments = [str(segment) for segment in args if segment]
    path = "/".join(segments)
    return path


#
# Generic utils
#

def extract(desired_keys, bigdict):
    subset = dict([(i, bigdict[i]) for i in desired_keys if i in bigdict])
    return subset

def get_file_path(current_filename, target_filename):
    """
    Returns the full file path for the target file.
    
    """
    current_dir = os.path.dirname(current_filename)
    file_path = os.path.normpath(os.path.join(current_dir, target_filename))
    return file_path

def coerce_id(_id):
    """
    Tries to coerce a vertex ID into an integer and returns it.

    :param v: The vertex ID we want to coerce into an integer.
    :type v: int or str

    :rtype: int or str

    """
    try:
        return int(_id)
    except:
        # some DBs, such as OrientDB, use string IDs
        return _id



