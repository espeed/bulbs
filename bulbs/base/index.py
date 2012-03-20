# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""

Bulbs supports pluggable backends. These are the abstract base classes that 
provides the index interface for a client. Implement these to create an index.

"""
from bulbs.utils import initialize_element, initialize_elements, get_one_result


# Index Proxies

class VertexIndexProxy(object):
    """
    Abstract base class the vertex index proxy.

    :ivar index_class: Index class.
    :ivar client: Client object.

    """
    def __init__(self, index_class, client):        
        # The index class for this proxy, e.g. ExactIndex.
        self.index_class = index_class

        # The Client object for the database.
        self.client = client
    
    def create(self, index_name):
        """
        Creates an Vertex index and returns it.

        :param index_name: Index name.
        :type index_name: str

        :rtype: Index
        
        """
        raise NotImplementedError

    def get(self, index_name):
        """
        Returns the Index object with the specified name or None if not found.
        
        :param index_name: Index name.
        :type index_name: str

        :rtype: Index
        
        """
        raise NotImplementedError

    def get_or_create(self, index_name):
        """
        Get a Vertex Index or create it if it doesn't exist.

        :param index_name: Index name.
        :type index_name: str

        :rtype: Index

        """ 
        raise NotImplementedError

    def delete(self, index_name):
        """ 
        Deletes an index and returns the Response.

        :param index_name: Index name.
        :type index_name: str

        :rtype: Response

        """
        raise NotImplementedError


class EdgeIndexProxy(object):
    """
    Abstract base class the edge index proxy.

    :ivar index_class: Index class.
    :ivar client: Client object.

    """
    def __init__(self, index_class, client):        
        # The index class for this proxy, e.g. ExactIndex.
        self.index_class = index_class

        # The Client object for the database.
        self.client = client
    
    def create(self, index_name):
        """
        Creates an Edge index and returns it.

        :param index_name: Index name.
        :type index_name: str

        :rtype: Index
        
        """
        raise NotImplementedError

    def get(self, index_name):
        """
        Returns the Index object with the specified name or None if not found.
        
        :param index_name: Index name.
        :type index_name: str

        :rtype: Index
        
        """
        raise NotImplementedError

    def get_or_create(self, index_name):
        """
        Get an Edge Index or create it if it doesn't exist.

        :param index_name: Index name.
        :type index_name: str

        :rtype: Index

        """ 
        raise NotImplementedError

    def delete(self, index_name):
        """ 
        Deletes an index and returns the Response.

        :param index_name: Index name.
        :type index_name: str

        :rtype: Response

        """
        raise NotImplementedError


# Index Containers

class Index(object):
    """
    Abstract base class for the default index.

    :ivar client: Client object 
    :ivar result: Result object.

    """

    def __init__(self, client, result):

        # The Client object for the database.
        self.client = client

        # The index attributes returned by the proxy request.
        self.result = result

    @classmethod 
    def get_proxy_class(cls, base_type=None):
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
        return self.result.get_index_name()

    @property
    def index_class(self):
        """
        Returns the index class.

        :rtype: class

        """
        return self.result.get_index_class()

    def put(self, _id, key=None, value=None, **pair):
        """
        Put an element into the index at key/value and return the Response.

        :param _id: The element ID.
        :type _id: int or str

        :param key: The index key. 
        :type key: str

        :param value: The key's value.
        :type value: str or int

        :param pair: Optional key/value pair. Example: name="James"
        :type pair: name/value pair

        :rtype: Response
            
        """
        raise NotImplementedError

    def update(self, _id, key=None, value=None, **pair):
        """
        Update the element ID for the key and value.
        
        :param key: The index key. 
        :type key: str

        :param value: The key's value.
        :type value: str or int

        :param pair: Optional key/value pair. Example: name="James"
        :type pair: key/value pair

        :rtype: Response

        """
        raise NotImplementedError

    def lookup(self, key=None, value=None, **pair):
        """
        Return all the elements in the index where key equals value.

        :param key: The index key. 
        :type key: str

        :param value: The key's value.
        :type value: str or int

        :param pair: Optional key/value pair. Example: name="James"
        :type pair: key/value pair

        :rtype: Element generator

        """
        raise NotImplementedError

    def put_unique(self, _id, key=None, value=None, **pair):
        """
        Put an element into the index at key/value and overwrite it if an 
        element already exists; thus, when you do a lookup on that key/value pair,
        there will be a max of 1 element returned.

        :param key: The index key. 
        :type key: str

        :param value: The key's value.
        :type value: str or int

        :param pair: Optional key/value pair. Example: name="James"
        :type pair: key/value pair

        :rtype: Resposne

        """
        raise NotImplementedError

    def get_unique(self, key=None, value=None, **pair):
        """
        Returns a max of 1 elements in the index matching the key/value pair.

        :param key: The index key. 
        :type key: str

        :param value: The key's value.
        :type value: str or int

        :param pair: Optional key/value pair. Example: name="James"
        :type pair: key/value pair

        :rtype: Element or None

        """
        raise NotImplementedError

    def remove(self, _id, key=None, value=None, **pair):
        """
        Remove the element from the index located by key/value.

        :param key: The index key. 
        :type key: str

        :param value: The key's value.
        :type value: str or int

        :param pair: Optional key/value pair. Example: name="James"
        :type pair: key/value pair

        :rtype: Response

        """
        raise NotImplementedError

    def count(self, key=None, value=None, **pair):
        """
        Return the number of items in the index for the key and value.

        :param key: The index key. 
        :type key: str

        :param value: The key's value.
        :type value: str or int

        :param pair: Optional key/value pair. Example: name="James"
        :type pair: name/value pair

        :rtype: int

        """
        raise NotImplementedError
        
    def _get_key_value(self, key, value, pair):
        """
        Returns the key and value, regardless of how it was entered.

        :param key: The index key. 
        :type key: str

        :param value: The key's value.
        :type value: str or int

        :param pair: Optional key/value pair. Example: name="James"
        :type pair: key/value pair

        :rtype: tuple

        """
        if pair:
            key, value = pair.popitem()
        return key, value

    def _get_method(self, **method_map):
        """
        Returns the right method, depending on the index class type.

        :param method_map: Dict mapping the index class type to its method name. 
        :type method_map: dict

        :rtype: Callable

        """
        method_name = method_map[self.index_class]
        method = getattr(self.client, method_name)
        return method
