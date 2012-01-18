# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
An interface for interacting with indices on Neo4j Server.

"""
from bulbs.utils import initialize_element, initialize_elements, get_one_result


class IndexProxy(object):
    """Abstract base class the index proxies."""

    def __init__(self,index_class,resource):        
        #: The index class for this proxy, e.g. ExactIndex.
        self.index_class = index_class

        #: The Resource object for the database.
        self.resource = resource
    
    def _build_index_config(self,index_class):
        assert self.index_class.blueprints_type is not "AUTOMATIC"
        index_config = {'type':self.index_class.index_type,
                        'provider':self.index_class.index_provider}
        return index_config
    

class VertexIndexProxy(IndexProxy):

    def create(self,index_name):
        """Creates an an index and returns it."""
        index_config = self._build_index_config(self.index_class)
        resp = self.resource.create_vertex_index(index_name,index_config)
        index = self.index_class(self.resource,resp.results)
        self.resource.registry.add_index(index_name,index)
        return index

    def get(self,index_name):
        """Returns the Index object with the specified name or None if not found."""
        resp = self.resource.get_vertex_index(index_name)
        if resp.results:
            index = self.index_class(self.resource,resp.results)
            self.resource.registry.add_index(index_name,index)
            return index

    def get_or_create(self,index_name):
        # get it, create if doesn't exist, then register it
        index = self.get(index_name)
        if not index:
            index = self.create(index_name)
        return index

    def delete(self,index_name):
        """Deletes/drops an index and returns the Rexster Response object."""
        return self.resource.delete_vertex_index(index_name)


class EdgeIndexProxy(IndexProxy):

    def create(self,index_name):
        """Creates an an index and returns it."""
        index_config = self._build_index_config(self.index_class)
        resp = self.resource.create_edge_index(index_name,index_config)
        index = self.index_class(self.resource,resp.results)
        self.resource.registry.add_index(index_name,index)
        return index

    def get(self,index_name):
        """Returns the Index object with the specified name or None if not found."""
        resp = self.resource.get_edge_index(index_name)
        if resp.results:
            index = self.index_class(self.resource,resp.results)
            self.resource.registry.add_index(index_name,index)
            return index

    def get_or_create(self,index_name,*args,**kwds):
        # get it, create if doesn't exist, then register it
        index = self.get(index_name)
        if not index:
            index = self.create(index_name,*args,**kwds)
        return index

    def delete(self,index_name):
        """Deletes/drops an index and returns the Rexster Response object."""
        return self.resource.delete_edge_index(index_name)

#
# Index Containers (Exact, Fulltext, Automatic)
#

class Index(object):
    """Abstract base class for Neo4j's Lucene index."""

    index_type = None
    index_provider = None
    blueprints_type = None

    def __init__(self,resource,results):
        self.resource = resource
        self.results = results

    @property
    def index_name(self):
        """Returns the index name."""
        return self.results.get('name')

    @property
    def index_class(self):
        """Returns the index class."""
    #    #print self.results.raw
        return self.results.get_index_class()

    def count(self,key=None,value=None,**pair):
        key, value = self._get_key_value(key,value,pair)
        script = self.resource.scripts.get('index_count')
        params = dict(index_name=self.index_name,key=key,value=value)
        resp = self.resource.gremlin(script,params)
        total_size = int(resp.content)
        return total_size


    def _get_key_value(self,key,value,pair):
        if pair:
            key, value = pair.popitem()
        return key, value


class ExactIndex(Index):

    index_type = "exact"
    index_provider = "lucene"
    blueprints_type = "MANUAL"

    def put(self,_id,key=None,value=None,**pair):
        """Put an element into the index at key/value and return the response."""
        # NOTE: if you ever change the _id arg to element, change remove() too
        key, value = self._get_key_value(key,value,pair)
        method_map = dict(vertex=self.resource.put_vertex,
                          edge=self.resource.put_edge)
        put_method = method_map.get(self.index_class)
        resp = put_method(self.index_name,key,value,_id)
        return resp

    def put_unique(self,_id,key=None,value=None,**pair):
        """
        Put an element into the index at key/value and overwrite it if an 
        element already exists at that key and value; thus, there will be a max
        of 1 element returned for that key/value pair. Return Rexster's 
        response.
        """
        return self.update(_id,key,value,**pair)

    def update(self,_id,key=None,value=None,**pair):
        """Update the element ID for the key and value."""

        # This should be a Gremlin method

        key, value = self._get_key_value(key,value,pair)
        method_map = dict(vertex=self.resource.remove_vertex,
                          edge=self.resource.remove_edge)
        remove_method = method_map.get(self.index_type)
        for result in self.get(key,value):
            remove_method(self.index_name,result._id,key,value)
        resp = self.put(_id,key,value)
        return resp


    def get(self,key=None,value=None,**pair):
        """Return all the elements with key property equal to value in the index."""
        key, value = self._get_key_value(key,value,pair)
        resp = self.resource.lookup_vertex(self.index_name,key,value)
        return initialize_elements(self.resource,resp)

    def get_unique(self,key=None,value=None,**pair):
        """Returns a max of 1 elements matching the key/value pair in the index."""
        key, value = self._get_key_value(key,value,pair)
        resp = self.resource.lookup_vertex(self.index_name,key,value)
        result = utils.get_one_result(resp)
        return initialize_element(self.resource,result)
         
    def query(self,query_string):
        pass

    def remove(self,_id,key=None,value=None,**pair):
        """Remove the element from the index located by key/value."""
        key, value = self._get_key_value(key,value,pair)
        method_map = dict(vertex=self.resource.remove_vertex,
                          edge=self.resource.remove_edge)
        remove_method = method_map.get(self.index_class)
        return remove_method(self.index_name,_id,key,value)


class FulltextIndex(Index):
    
    index_type = "fulltext"
    index_provider = "lucene"
    blueprints_type = "MANUAL"

    def query(self,query_string):
        """
        Return elements mathing the query.

        :param query_string: The query formatted in the Lucene query language. 
        
        See http://lucene.apache.org/java/3_1_0/queryparsersyntax.html

        """
        resp = self.resource.query_fulltext_index(self.index_name,query_string)
        return initialize_elements(self.resource,resp)

class AutomaticIndex(Index):

    index_type = "exact"
    index_provider = "lucene"
    blueprints_type = "AUTOMATIC"

    def get(self,key=None,value=None,**pair):
        """Return all the elements with key property equal to value in the index."""
        key, value = self._get_key_value(key,value,pair)
        resp = self.resource.lookup_vertex(self.index_name,key,value)
        return initialize_elements(self.resource,resp)

    def query(self,query_string):
        pass


