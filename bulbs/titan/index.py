# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
An interface for interacting with indices on Rexster.

"""
from bulbs.utils import initialize_element, initialize_elements, get_one_result


class IndexProxy(object):
    """Abstract base class the index proxies."""

    def __init__(self, index_class, client):        
        # The index class for this proxy, e.g. ManualIndex.
        self.index_class = index_class

        # The Client object for the database.
        self.client = client
    

class VertexIndexProxy(IndexProxy):
    """
    Manage vertex indices on Rexster.

    :param index_class: The index class for this proxy, e.g. ManualIndex.
    :type index_class: Index

    :param client: The Client object for the database.
    :type client: bulbs.rexster.client.RexsterClient

    :ivar index_class: Index class.
    :ivar client: RexsterClient object.

    """
                        
    def create(self, index_name):
        """
        Creates an Vertex index and returns it.

        :param index_name: Index name.
        :type index_name: str

        :rtype: bulbs.rexster.index.Index
        
        """
        raise NotImplementedError

    def get(self, index_name="vertex"):
        """
        Returns the Index object with the specified name or None if not found.
        
        :param index_name: Index name.
        :type index_name: str

        :rtype: bulbs.rexster.index.Index
        
        """
        index = self.index_class(self.client, None)
        index.base_type = "vertex"
        index._index_name = index_name
        self.client.registry.add_index(index_name, index)
        return index

    def get_or_create(self, index_name="vertex", index_params=None):
        """
        Get a Vertex Index or create it if it doesn't exist.

        :param index_name: Index name.
        :type index_name: str

        :rtype: bulbs.rexster.index.Index

        """ 
        return self.get(index_name)

    def delete(self, index_name):
        """ 
        Deletes an index and returns the Response.

        :param index_name: Index name.
        :type index_name: str

        :rtype: bulbs.rexster.client.RexsterResponse

        """
        raise NotImplementedError


class EdgeIndexProxy(IndexProxy):
    """
    Manage edge indices on Rexster.

    :param index_class: The index class for this proxy, e.g. ManualIndex.
    :type index_class: Index

    :param client: The Client object for the database.
    :type client: bulbs.rexster.client.RexsterClient

    :ivar index_class: Index class.
    :ivar client: RexsterClient object.

    """

    def create(self,index_name,*args,**kwds):
        """ 
        Adds an index to the database and returns it. 

        index_keys must be a string in this format: '[k1,k2]'
        Don't pass actual list b/c keys get double quoted.

        :param index_name: The name of the index to create.

        :param index_class: The class of the elements stored in the index. 
                            Either vertex or edge.
        
        """
        raise NotImplementedError

    def get(self, index_name="edge"):
        """
        Returns the Index object with the specified name or None if not found.
        
        :param index_name: Index name.
        :type index_name: str

        :rtype: bulbs.rexster.index.Index
        
        """
        index = self.index_class(self.client, None)
        index.base_type = "edge"
        index._index_name = index_name
        self.client.registry.add_index(index_name, index)
        return index


    def get_or_create(self, index_name="edge", index_params=None):
        """
        Get an Edge Index or create it if it doesn't exist.

        :param index_name: Index name.
        :type index_name: str

        :rtype: bulbs.rexster.index.Index

        """ 
        return self.get(index_name)

    def delete(self,index_name):
        """ 
        Deletes an index and returns the Response.

        :param index_name: Index name.
        :type index_name: str

        :rtype: bulbs.rexster.client.RexsterResponse

        """
        raise NotImplementedError

#
# Index Containers (Titan only supports KeyIndex so far)
#

class Index(object):
    """Abstract base class for an index."""

    def __init__(self, client, result):
        self.client = client
        self.result = result
        self.base_type = None # set by Factory.get_index
        self._index_name = None # ditto 
        # the index_name is actually ignored with Titan, 
        # but setting it like normal to make tests pass

    @classmethod 
    def get_proxy_class(cls, base_type):
        """
        Returns the IndexProxy class.

        :param base_type: Index base type, either vertex or edge.
        :type base_type: str

        :rtype: class

        """
        class_map = dict(vertex=VertexIndexProxy, edge=EdgeIndexProxy)
        return class_map[base_type]

    @property
    def index_name(self):
        """
        Returns the index name.

        :rtype: str

        """
        # faking the index name as "vertex"
        return self._index_name

    @property
    def index_class(self):
        """
        Returns the index class, either vertex or edge.

        :rtype: class

        """
        return self.base_type
    
    @property
    def index_type(self):
        """
        Returns the index type, which will either be automatic or manual.

        :rtype: str

        """
        return "automatic"

    def count(self,key=None,value=None,**pair):
        """
        Return a count of all elements with 'key' equal to 'value' in the index.

        :param key: The index key. This is optional because you can instead 
                    supply a key/value pair such as name="James". 

        :param value: The index key's value. This is optional because you can 
                      instead supply a key/value pair such as name="James". 

        :param pair: Optional keyword param. Instead of supplying key=name 
                     and value = 'James', you can supply a key/value pair in
                     the form of name='James'.
        """
        raise NotImplementedError


    def _get_key_value(self, key, value, pair):
        """Return the key and value, regardless of how it was entered."""
        if pair:
            key, value = pair.popitem()
        return key, value

    def _get_method(self, **method_map):
        method_name = method_map[self.index_class]
        method = getattr(self.client, method_name)
        return method

    def lookup(self, key=None, value=None, **pair):
        """
        Return a generator containing all the elements with key property equal 
        to value in the index.

        :param key: The index key. This is optional because you can instead 
                    supply a key/value pair such as name="James". 

        :param value: The index key's value. This is optional because you can 
                      instead supply a key/value pair such as name="James". 

        :param raw: Optional keyword param. If set to True, it won't try to 
                    initialize the results. Defaults to False. 

        :param pair: Optional keyword param. Instead of supplying key=name 
                     and value = 'James', you can supply a key/value pair in
                     the form of name='James'.
        """
        key, value = self._get_key_value(key, value, pair)
        resp = self.client.lookup_vertex(self.index_name,key,value)
        return initialize_elements(self.client,resp)


    def get_unique(self,key=None,value=None,**pair):
        """
        Returns a max of 1 elements matching the key/value pair in the index.

        :param key: The index key. This is optional because you can instead 
                    supply a key/value pair such as name="James". 

        :param value: The index key's value. This is optional because you can 
                      instead supply a key/value pair such as name="James". 

        :param pair: Optional keyword param. Instead of supplying key=name 
                     and value = 'James', you can supply a key/value pair in
                     the form of name='James'.
        """
        key, value = self._get_key_value(key,value,pair)
        resp = self.client.lookup_vertex(self.index_name,key,value)
        if resp.total_size > 0:
            result = get_one_result(resp)
            return initialize_element(self.client, result)

class KeyIndex(Index):

    def keys(self):
        """Return the index's keys."""
        # Titan does not support edge indices.
        resp = self.client.get_vertex_keys()
        return [result.raw for result in resp.results]

    def create_key(self, key):
        # TODO: You can't create a key if prop already exists - workaround?
        if self.base_type is "edge":
            return self.create_edge_key(key)
        return self.create_vertex_key(key)
                        
    def create_vertex_key(self, key):
        return self.client.create_vertex_key_index(key)        

    def create_edge_key(self, key):
        return self.client.create_vertex_key_index(key)

    def rebuild(self):
        raise NotImplementedError # (for now)
        # need class_map b/c the Blueprints need capitalized class names, 
        # but Rexster returns lower-case class names for index_class
        method_map = dict(vertex=self.client.rebuild_vertex_index,
                          edge=self.client.rebuild_edge_index)
        rebuild_method = method_map.get(self.index_class)
        resp = rebuild_method(self.index_name)
        return list(resp.results)
        

 
