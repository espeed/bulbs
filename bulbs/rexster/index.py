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
        resp = self.client.create_vertex_index(index_name)
        index = self.index_class(self.client,resp.results)
        self.client.registry.add_index(index_name, index)
        return index

    def get(self, index_name):
        """
        Returns the Index object with the specified name or None if not found.
        
        :param index_name: Index name.
        :type index_name: str

        :rtype: bulbs.rexster.index.Index
        
        """
        resp = self.client.get_vertex_index(index_name)
        if resp.results:
            index = self.index_class(self.client,resp.results)
            self.client.registry.add_index(index_name, index)
            return index

    def get_or_create(self, index_name, index_params=None):
        """
        Get a Vertex Index or create it if it doesn't exist.

        :param index_name: Index name.
        :type index_name: str

        :rtype: bulbs.rexster.index.Index

        """ 
        resp = self.client.get_or_create_vertex_index(index_name, index_params)
        index = self.index_class(self.client,resp.results)
        self.client.registry.add_index(index_name, index)
        return index

    def delete(self, index_name):
        """ 
        Deletes an index and returns the Response.

        :param index_name: Index name.
        :type index_name: str

        :rtype: bulbs.rexster.client.RexsterResponse

        """
        try:
            return self.client.delete_vertex_index(index_name)
        except LookupError:
            return None


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
        resp = self.client.create_edge_index(index_name,*args,**kwds)
        index = self.index_class(self.client,resp.results)
        self.client.registry.add_index(index_name,index)
        return index

    def get(self,index_name):
        """
        Returns the Index object with the specified name or None if not found.
        
        :param index_name: Index name.
        :type index_name: str

        :rtype: bulbs.rexster.index.Index
        
        """
        resp = self.client.get_edge_index(index_name)
        if resp.results:
            index = self.index_class(self.client,resp.results)
            self.client.registry.add_index(index_name,index)
            return index

    def get_or_create(self, index_name, index_params=None):
        """
        Get an Edge Index or create it if it doesn't exist.

        :param index_name: Index name.
        :type index_name: str

        :rtype: bulbs.rexster.index.Index

        """ 
        resp = self.client.get_or_create_edge_index(index_name, index_params)
        index = self.index_class(self.client,resp.results)
        self.client.registry.add_index(index_name, index)
        return index

    def delete(self,index_name):
        """ 
        Deletes an index and returns the Response.

        :param index_name: Index name.
        :type index_name: str

        :rtype: bulbs.rexster.client.RexsterResponse

        """
        try:
            return self.client.delete_edge_index(index_name)
        except LookupError:
            return None


#
# Index Containers (Manual, Automatic)
#

class Index(object):
    """Abstract base class for an index."""

    def __init__(self, client, result):
        self.client = client
        self.result = result

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
        return self.result.data['name']

    @property
    def index_class(self):
        """
        Returns the index class, either vertex or edge.

        :rtype: class

        """
        return self.result.data['class']

    @property
    def index_type(self):
        """
        Returns the index type, which will either be automatic or manual.

        :rtype: str

        """
        return self.result.data['type']

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
        key, value = self._get_key_value(key,value,pair)
        resp = self.client.index_count(self.index_name,key,value)
        return resp.content['totalSize']


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


class ManualIndex(Index):
    """
    Creates, retrieves, and deletes indices provided by the graph database.

    Use this class to get, put, and update items in an index.
    

    :param client: The Client object for the database.

    :param result: The result list returned by Rexster.

    :param classes: Zero or more subclasses of Element to use when 
                    initializing the the elements returned by the query. 
                    For example, if Person is a subclass of Node (which 
                    is defined in model.py and is a subclass of Vertex), 
                    and the query returns person elements, pass in the 
                    Person class and the method will use the element_type
                    defined in the class to initialize the returned items
                    to a Person object.

    Example that creates an index for Web page URL stubs, 
    adds an page element to it, and then retrieves it from the index::

        >>> graph = Graph()
        >>> graph.indices.create("page","vertex","automatic","[stub]")
        >>> index = graph.indices.get("page")
        >>> index.put("stub",stub,page._id)
        >>> page = index.get("stub",stub)

    """

    
    def put(self,_id,key=None,value=None,**pair):
        """
        Put an element into the index at key/value and return Rexster's 
        response.

        :param _id: The element ID.

        :param key: The index key. This is optional because you can instead 
                    supply a key/value pair such as name="James". 

        :param value: The index key's value. This is optional because you can 
                      instead supply a key/value pair such as name="James". 

        :param pair: Optional keyword param. Instead of supplying key=name 
                     and value = 'James', you can supply a key/value pair in
                     the form of name='James'.

        """
        # NOTE: if you ever change the _id arg to element, change remove() too
        key, value = self._get_key_value(key,value,pair)
        put = self._get_method(vertex="put_vertex", edge="put_edge")
        resp = put(self.index_name,key,value,_id)
        return resp

    def update(self,_id,key=None,value=None,**pair):
        """
        Update the element ID for the key and value and return Rexsters' 
        response.

        :param _id: The element ID.

        :param key: The index key. This is optional because you can instead 
                    supply a key/value pair such as name="James". 

        :param value: The index key's value. This is optional because you can 
                      instead supply a key/value pair such as name="James". 

        :param pair: Optional keyword param. Instead of supplying key=name 
                     and value = 'James', you can supply a key/value pair in
                     the form of name='James'.
        """
        key, value = self._get_key_value(key,value,pair)
        for result in self.get(key,value):
            self.remove(self.index_name, result._id, key, value)
        return self.put(_id,key,value)


    def put_unique(self,_id,key=None,value=None,**pair):
        """
        Put an element into the index at key/value and overwrite it if an 
        element already exists at that key and value; thus, there will be a max
        of 1 element returned for that key/value pair. Return Rexster's 
        response.

        :param _id: The element ID.

        :param key: The index key. This is optional because you can instead 
                    supply a key/value pair such as name="James". 

        :param value: The index key's value. This is optional because you can 
                      instead supply a key/value pair such as name="James". 

        :param pair: Optional keyword param. Instead of supplying key=name 
                     and value = 'James', you can supply a key/value pair in 
                     the form of name='James'.

        """
        return self.update(_id, key, value, **pair)


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

    def remove(self,_id,key=None,value=None,**pair):
        """
        Remove the element from the index located by key/value.

        :param _id: The element ID.

        :param key: The index key. This is optional because you can instead 
                    supply a key/value pair such as name="James". 

        :param value: The index key's value. This is optional because you can 
                      instead supply a key/value pair such as name="James". 

        :param pair: Optional keyword param. Instead of supplying key=name 
                     and value = 'James', you can supply a key/value pair in
                     the form of name='James'.
        """
        key, value = self._get_key_value(key, value, pair)
        remove = self._get_method(vertex="remove_vertex", edge="remove_edge")
        return remove(self.index_name,_id,key,value)


class AutomaticIndex(Index):

    def keys(self):
        """Return the index's keys."""
        resp = self.client.index_keys(self.index_name)
        return list(resp.results)
    
    def rebuild(self):
        # need class_map b/c the Blueprints need capitalized class names, 
        # but Rexster returns lower-case class names for index_class
        method_map = dict(vertex=self.client.rebuild_vertex_index,
                          edge=self.client.rebuild_edge_index)
        rebuild_method = method_map.get(self.index_class)
        resp = rebuild_method(self.index_name)
        return list(resp.results)

 
