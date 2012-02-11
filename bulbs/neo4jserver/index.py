# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
An interface for interacting with indices on Neo4j Server.

"""
from bulbs.utils import initialize_element, initialize_elements, get_one_result


class IndexProxy(object):
    """Abstract base class the index proxies."""

    def __init__(self,index_class,client):        
        #: The index class for this proxy, e.g. ExactIndex.
        self.index_class = index_class

        #: The Client object for the database.
        self.client = client
    
    def _build_index_config(self,index_class):
        assert self.index_class.blueprints_type is not "AUTOMATIC"
        index_config = {'type':self.index_class.index_type,
                        'provider':self.index_class.index_provider}
        return index_config
    

class VertexIndexProxy(IndexProxy):
    """Manage vertex indices on Neo4j Server."""

    def create(self, index_name):
        """Creates an an index and returns it."""
        index_config = self._build_index_config(self.index_class)
        resp = self.client.create_vertex_index(index_name,index_config)
        index = self.index_class(self.client,resp.results)
        self.client.registry.add_index(index_name,index)
        return index

    def get(self, index_name):
        """Returns the Index object with the specified name or None if not found."""
        resp = self.client.get_vertex_index(index_name)
        if resp.results:
            index = self.index_class(self.client,resp.results)
            self.client.registry.add_index(index_name,index)
            return index

    def get_or_create(self, index_name):
        """Get a vertex index or creates it if it doesn't exist.""" 
        index = self.get(index_name)
        if not index:
            index = self.create(index_name)
        return index

    def delete(self, index_name):
        """Deletes/drops an index and returns the Response."""
        return self.client.delete_vertex_index(index_name)


class EdgeIndexProxy(IndexProxy):
    """Manage edge indices on Neo4j Server."""

    def create(self, index_name):
        """Creates an an index and returns it."""
        index_config = self._build_index_config(self.index_class)
        resp = self.client.create_edge_index(index_name,index_config)
        index = self.index_class(self.client,resp.results)
        self.client.registry.add_index(index_name,index)
        return index

    def get(self, index_name):
        """Returns the Index object with the specified name or None if not found."""
        resp = self.client.get_edge_index(index_name)
        if resp.results:
            index = self.index_class(self.client,resp.results)
            self.client.registry.add_index(index_name,index)
            return index

    def get_or_create(self, index_name, *args, **kwds):
        """Get an edge index or creates it if it doesn't exist.""" 
        index = self.get(index_name)
        if not index:
            index = self.create(index_name, *args, **kwds)
        return index

    def delete(self, index_name):
        """Deletes/drops an index and returns the Response."""
        return self.client.delete_edge_index(index_name)

#
# Index Containers (Exact, Unique, Fulltext, Automatic)
#

class Index(object):
    """Abstract base class for Neo4j's Lucene index."""

    index_type = None
    index_provider = None
    blueprints_type = None

    def __init__(self,client,results):
        self.client = client
        self.results = results

    @classmethod 
    def get_proxy_class(cls, base_type=None):
        class_map = dict(vertex=VertexIndexProxy, edge=EdgeIndexProxy)
        return class_map[base_type]

    @property
    def index_name(self):
        """Returns the index name."""
        return self.results.get_index_name()

    @property
    def index_class(self):
        """Returns the index class."""
        return self.results.get_index_class()

    def count(self, key=None, value=None, **pair):
        """Return the number of items in the index for the key and value."""
        key, value = self._get_key_value(key,value,pair)
        script = self.client.scripts.get('index_count')
        params = dict(index_name=self.index_name,key=key,value=value)
        resp = self.client.gremlin(script,params)
        total_size = int(resp.content)
        return total_size

    def _get_key_value(self, key, value, pair):
        """Return the key and value, regardless of how it was entered."""
        if pair:
            key, value = pair.popitem()
        return key, value

    def _get_method(self, **method_map):
        method_name = method_map[self.index_class]
        method = getattr(self.client, method_name)
        return method

class FulltextIndex(Index):
    
    index_type = "fulltext"
    index_provider = "lucene"
    blueprints_type = "MANUAL"

    def query(self, query_string):
        """
        Return elements mathing the query.

        :param query_string: The query formatted in the Lucene query language. 
        
        See http://lucene.apache.org/java/3_1_0/queryparsersyntax.html

        """
        resp = self.client.query_fulltext_index(self.index_name,query_string)
        return initialize_elements(self.client,resp)

class ExactIndex(Index):

    index_type = "exact"
    index_provider = "lucene"
    blueprints_type = "MANUAL"

    def put(self, _id, key=None, value=None, **pair):
        """Put an element into the index at key/value and return the response."""
        key, value = self._get_key_value(key,value,pair)
        put = self._get_method(vertex="put_vertex", edge="put_edge")
        return put(self.index_name,key,value,_id)

    def update(self, _id, key=None, value=None, **pair):
        """Update the element ID for the key and value."""
        # This should be a Gremlin method
        key, value = self._get_key_value(key,value,pair)
        for result in self.get(key,value):
            self.remove(self.index_name, result._id, key, value)
        return self.put(_id,key,value)

    def lookup(self, key=None, value=None, **pair):
        """Return all the elements with key property equal to value in the index."""
        key, value = self._get_key_value(key,value,pair)
        lookup = self._get_method(vertex="lookup_vertex", edge="lookup_edge")
        resp = lookup(self.index_name,key,value)
        return initialize_elements(self.client,resp)

    def query(self, query_string):
        pass

    def remove(self, _id, key=None, value=None, **pair):
        """Remove the element from the index located by key/value."""
        key, value = self._get_key_value(key,value,pair)
        remove = self._get_method(vertex="remove_vertex", edge="remove_edge")
        return remove(self.index_name,_id,key,value)

# uncdocumented -- experimental
class UniqueIndex(ExactIndex):

    def put(self, _id, key=None, value=None, **pair):
        """
        Put an element into the index at key/value and overwrite it if an 
        element already exists at that key and value; thus, there will be a max
        of 1 element returned for that key/value pair. Return Rexster's 
        response.
        """
        return self.update(_id, key, value, **pair)

    def lookup(self, key=None, value=None, **pair):
        """Returns a max of 1 elements matching the key/value pair in the index."""
        key, value = self._get_key_value(key,value,pair)
        lookup = self._get_method(vertex="lookup_vertex", edge="lookup_edge")
        resp = lookup(self.index_name,key,value)
        result = get_one_result(resp)
        if result:
            return initialize_element(self.client,result)
   
# uncdocumented -- experimental
class AutomaticIndex(ExactIndex):

    index_type = "exact"
    index_provider = "lucene"
    blueprints_type = "AUTOMATIC"

    # This works just like an ExactIndex except that the put, update, remove methods
    # are not implemented because those are done automatically.

    def put(self,_id, key=None, value=None, **pair):
        raise NotImplementedError

    def update(self, _id, key=None, value=None, **pair):
        raise NotImplementedError

    def remove(self, _id, key=None, value=None, **pair):
        raise NotImplementedError

