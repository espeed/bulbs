# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""

Bulbs supports pluggable backends. These are the abstract base classes that 
provides the index interface for a resource. Implement these to create an index.

"""
from bulbs.utils import initialize_element, initialize_elements, get_one_result


class IndexProxy(object):
    """Abstract base class the index proxies."""

    def __init__(self,index_class,resource):        
        #: The index class for this proxy, e.g. ExactIndex.
        self.index_class = index_class

        #: The Resource object for the database.
        self.resource = resource
    
    def create(self,index_name,*args,**kwds):
        """Creates an an index and returns it."""
        raise NotImplementedError

    def get(self,index_name):
        """Returns the Index object with the specified name or None if not found."""
        raise NotImplementedError

    def get_or_create(self,index_name,*args,**kwds):
        # get it, create if doesn't exist, then register it
        raise NotImplementedError

    def delete(self,index_name):
        """Deletes/drops an index and returns the Rexster Response object."""
        raise NotImplementedError


class Index(object):
    """Abstract base class for Neo4j's Lucene index."""

    def __init__(self,resource,results):

        #: The Resource object for the database.
        self.resource = resource

        #: The index attributes returned by the proxy request.
        self.results = results

    @property
    def index_name(self):
        """Returns the index name."""        
        raise NotImplementedError

    def put(self,_id,key=None,value=None,**pair):
        """Put an element into the index at key/value and return the response."""
        raise NotImplementedError

    def put_unique(self,_id,key=None,value=None,**pair):
        """
        Put an element into the index at key/value and overwrite it if an 
        element already exists at that key and value; thus, there will be a max
        of 1 element returned for that key/value pair. Return Rexster's 
        response.
        """
        raise NotImplementedError

    def update(self,_id,key=None,value=None,**pair):
        """Update the element ID for the key and value."""
        raise NotImplementedError

    def get(self,key=None,value=None,**pair):
        """Return all the elements with key property equal to value in the index."""
        raise NotImplementedError

    def get_unique(self,key=None,value=None,**pair):
        """Returns a max of 1 elements matching the key/value pair in the index."""
        raise NotImplementedError

    def remove(self,_id,key=None,value=None,**pair):
        """Remove the element from the index located by key/value."""
        raise NotImplementedError
