# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
import os
import sys
import inspect
import logging
import numbers
import codecs

import time
import datetime
import calendar
import omnijson as json # supports Python 2.5-3.2



#
# Python 3 
#

if sys.version < '3':
#    import ujson as json
    from urllib import quote, quote_plus, urlencode
    from urlparse import urlsplit, urlparse

    # def u(x):
    #     return codecs.unicode_escape_decode(x)[0]

                
else:
    # ujson is faster but hasn't been ported to Python 3 yet
#    import json
    from urllib.parse import quote, quote_plus, urlencode, urlparse
    from urllib.parse import urlsplit

    long = int
    unicode = str

    # def u(x):
    #     return x

# NOTE: now using the same unicode func for both Python 2 and Python 3
# http://stackoverflow.com/questions/6625782/unicode-literals-that-work-in-python-3-and-2
# Unicode - see Armin's http://lucumr.pocoo.org/2013/7/2/the-updated-guide-to-unicode/
def u(x):
    byte_string, length = codecs.unicode_escape_encode(x)
    unicode_string, length = codecs.unicode_escape_decode(x)
    return unicode_string



#
# Logging
#

bulbs_logger = logging.getLogger('bulbs')

def get_logger(name, level=None):
    #logger = logging.getLogger(name)
    logger = bulbs_logger.getChild(name)
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
        # yield doesn't work for conditionals
        return (initialize_element(client, result) for result in response.results)

def initialize_element(client,result):
    # result should be a single Result object, not a list or generator
    element_class = get_element_class(client,result)
    element = element_class(client)
    element._initialize(result)
    return element

def get_element_class(client,result):
    element_key = get_element_key(client,result)
    element_class = client.registry.get_class(element_key)
    if element_class is None:
        # if element_class is not in registry, return the generic Vertex/Edge class
        base_type = result.get_type()
        element_class = client.registry.get_class(base_type)
    return element_class

def get_element_key(client,result):
    var_map = dict(vertex=client.config.type_var,
                   edge=client.config.label_var)
    base_type = result.get_type()
    if base_type == "vertex":
        key_var = var_map[base_type]
        # if key_var not found, just return the generic type for the Vertex
        element_key = result.data.get(key_var, base_type)
    elif base_type == "edge":
        label = result.get_label()
        element_key = label if label in client.registry.class_map else base_type
    else:
        raise TypeError
    return element_key

# Deprecated in favor of resp.one()
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
    

def get_key_value(key, value, pair):
    """Return the key and value, regardless of how it was entered."""
    if pair:
        key, value = pair.popitem()
    return key, value


#
# Client Utils
#


def build_path(*args):
    # don't include segment if it's None
    # quote_plus doesn't work for neo4j index lookups;
    # for example, this won't work: index/node/test_idxV/name/James+Thornton
    segments = [quote(u(to_string(segment)), safe='') for segment in args if segment is not None]
    path = "/".join(segments)
    return path

def to_string(value):
    # maybe convert a number to a string
    return value if not isinstance(value, numbers.Number) else str(value)
   

#
# Time Utils
#

def current_timestamp():
    # Return the unix UTC time 
    # TODO: should we cast this to an int for consistency?
    return int(time.time())

def current_datetime():
    # Returns a UTC datetime object
    # return datetime.datetime.utcnow()
    now =  current_timestamp()
    #return datetime.datetime.utcfromtimestamp(now).replace(tzinfo=pytz.utc)
    return datetime.datetime.utcfromtimestamp(now)

def current_date():
    #Return  a date object
    return to_date(current_timestamp())
    
def to_timestamp(datetime):
    # Converts a datetime object to unix UTC time
    return calendar.timegm(datetime.utctimetuple()) 

def to_datestamp(date):
    # Converts a date object to unix UTC time
    return calendar.timegm(date.timetuple()) 

def to_datetime(timestamp):
    # Converts unix UTC time into a UTC datetime object
    #return datetime.datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
    return datetime.datetime.utcfromtimestamp(timestamp)

def to_date(timestamp):
    # Converts unix UTC time into a date object
    return datetime.date.fromtimestamp(timestamp)
    
# Exaplanations on dealing with time...

    # http://unix4lyfe.org/time/
    # http://lucumr.pocoo.org/2011/7/15/eppur-si-muove/
    # http://nvie.com/posts/introducing-times/
    # http://news.ycombinator.com/item?id=3545935
    # http://labix.org/python-dateutil
    # http://docs.python.org/library/time.html#module-time
    # http://code.davidjanes.com/blog/2008/12/22/working-with-dates-times-and-timezones-in-python/

    # for historical dates, see:
    # http://www.egenix.com/products/python/mxBase/mxDateTime/

    # Always store UTC

    # One way (I think dateutils requires this)
    # t = time.time()  # unix utc timestamp
    # dt = datetime.datetime.utcfromtimestamp(t) 
    # ut = calendar.timegm(dt.utctimetuple()) 

    # Simpler way?
    # t = time.time()  # unix utc timestamp
    # dt = time.gmtime(t)
    # t = calendar.timegm(dt)

    # Both ways lose subsecond precision going from datetime object to unixtime    
    # t = time.mktime(dt)  # back to unix timestamp # don't use this, this is the inverse of localtime()



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




