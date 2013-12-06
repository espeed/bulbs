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

    def __init__(self, index_class, client):        
        # The index class for this proxy, e.g. ExactIndex.
        self.index_class = index_class

        # The Client object for the database.
        self.client = client
    
    def _build_index_config(self, index_class):
        assert self.index_class.blueprints_type is not "AUTOMATIC"
        index_config = {'type':self.index_class.index_type,
                        'provider':self.index_class.index_provider}
        return index_config
    

class VertexIndexProxy(IndexProxy):
    """
    Manage vertex indices on Neo4j Server.

    :param index_class: The index class for this proxy, e.g. ExactIndex.
    :type index_class: Index

    :param client: The Client object for the database.
    :type client: bulbs.neo4jserver.client.Neo4jClient

    :ivar index_class: Index class.
    :ivar client: Neo4jClient object.

    """
    def create(self, index_name):
        """
        Creates an Vertex index and returns it.

        :param index_name: Index name.
        :type index_name: str

        :rtype: bulbs.neo4jserver.index.Index
        
        """
        config = self._build_index_config(self.index_class)
        resp = self.client.create_vertex_index(index_name,index_config=config)
        index = self.index_class(self.client, resp.results)
        self.client.registry.add_index(index_name,index)
        return index

    def get(self, index_name):
        """
        Returns the Index object with the specified name or None if not found.
        
        :param index_name: Index name.
        :type index_name: str

        :rtype: bulbs.neo4jserver.index.Index
        
        """
        resp = self.client.get_vertex_index(index_name)
        if resp.results:
            index = self.index_class(self.client, resp.results)
            self.client.registry.add_index(index_name,index)
            return index

    def get_or_create(self, index_name):
        """
        Get a Vertex Index or create it if it doesn't exist.

        :param index_name: Index name.
        :type index_name: str

        :rtype: bulbs.neo4jserver.index.Index

        """ 
        config = self._build_index_config(self.index_class)
        resp = self.client.get_or_create_vertex_index(index_name,index_config=config)
        index = self.index_class(self.client, resp.results)
        self.client.registry.add_index(index_name,index)
        return index

    def delete(self, index_name):
        """ 
        Deletes an index and returns the Response.

        :param index_name: Index name.
        :type index_name: str

        :rtype: bulbs.neo4jserver.client.Neo4jResponse

        """
        return self.client.delete_vertex_index(index_name)


class EdgeIndexProxy(IndexProxy):
    """
    Manage edge indices on Neo4j Server.

    :param index_class: The index class for this proxy, e.g. ExactIndex.
    :type index_class: Index

    :param client: The Client object for the database.
    :type client: bulbs.neo4jserver.client.Neo4jClient

    :ivar index_class: Index class.
    :ivar client: Neo4jClient object.

    """
    def create(self, index_name):
        """
        Creates an Edge index and returns it.

        :param index_name: Index name.
        :type index_name: str

        :rtype: bulbs.neo4jserver.index.Index
        
        """
        config = self._build_index_config(self.index_class)
        resp = self.client.create_edge_index(index_name,index_config=config)
        index = self.index_class(self.client,resp.results)
        self.client.registry.add_index(index_name,index)
        return index

    def get(self, index_name):
        """
        Returns the Index object with the specified name or None if not found.
        
        :param index_name: Index name.
        :type index_name: str

        :rtype: bulbs.neo4jserver.index.Index
        
        """
        resp = self.client.get_edge_index(index_name)
        if resp.results:
            index = self.index_class(self.client,resp.results)
            self.client.registry.add_index(index_name,index)
            return index

    def get_or_create(self, index_name):
        """
        Get an Edge Index or create it if it doesn't exist.

        :param index_name: Index name.
        :type index_name: str

        :rtype: bulbs.neo4jserver.index.Index

        """ 
        config = self._build_index_config(self.index_class)
        resp = self.client.get_or_create_edge_index(index_name, index_config=config)
        index = self.index_class(self.client, resp.results)
        self.client.registry.add_index(index_name,index)
        return index

    def delete(self, index_name):
        """ 
        Deletes an index and returns the Response.

        :param index_name: Index name.
        :type index_name: str

        :rtype: bulbs.neo4jserver.client.Neo4jResponse

        """
        return self.client.delete_edge_index(index_name)

#
# Index Containers (Exact, Fulltext, Automatic, Unique)
#

class Index(object):
    """Abstract base class for Neo4j's Lucene index."""

    index_type = None
    index_provider = None
    blueprints_type = None

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
        return self.result.get_index_name()

    @property
    def index_class(self):
        """
        Returns the index class, either vertex or edge.

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

        :rtype: bulbs.neo4jserver.client.Neo4jResponse
            
        """
        key, value = self._get_key_value(key,value,pair)
        put = self._get_method(vertex="put_vertex", edge="put_edge")
        return put(self.index_name,key,value,_id)

    def update(self, _id, key=None, value=None, **pair):
        """
        Update the element ID for the key and value.
        
        :param key: The index key. 
        :type key: str

        :param value: The key's value.
        :type value: str or int

        :param pair: Optional key/value pair. Example: name="James"
        :type pair: key/value pair

        :rtype: bulbs.neo4jserver.client.Neo4jResponse

        """
        # TODO: This should be a Gremlin method
        key, value = self._get_key_value(key,value,pair)
        for result in self.get(key,value):
            self.remove(self.index_name, result._id, key, value)
        return self.put(_id,key,value)

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
        key, value = self._get_key_value(key,value,pair)
        lookup = self._get_method(vertex="lookup_vertex", edge="lookup_edge")
        resp = lookup(self.index_name,key,value)
        return initialize_elements(self.client, resp)

    #put_unique = update
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

        :rtype: bulbs.neo4jserver.client.Neo4jResponse

        """
        return self.update(_id, key, value, **pair)

    # TODO: maybe a putIfAbsent method too

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
        key, value = self._get_key_value(key,value,pair)
        lookup = self._get_method(vertex="lookup_vertex", edge="lookup_edge")
        resp = lookup(self.index_name,key,value)
        if resp.total_size > 0:
            result = get_one_result(resp)
            return initialize_element(self.client,result)

    def create_unique_vertex(self, key=None, value=None, data=None, **pair):
        """
        Returns a tuple containing two values. The first is the element if it
        was created / found. The second is a boolean value the tells whether
        the element was created (True) or not (False).

        :param key: The index key.
        :type key: str

        :param value: The key's value.
        :type value: str or int

        :param pair: Optional key/value pair. Example: name="James"
        :type pair: key/value pair

        :rtype: tuple

        """
        key, value = self._get_key_value(key,value,pair)
        data = {} if data is None else data
        create = self._get_method(vertex="create_unique_vertex")
        resp = create(self.index_name, key, value, data)
        if resp.total_size > 0:
            result = get_one_result(resp)
            was_created = resp.headers['status'] == '201'
            return initialize_element(self.client, result), was_created
        else:
            return None, False

    def remove(self, _id, key=None, value=None, **pair):
        """
        Remove the element from the index located by key/value.

        :param key: The index key. 
        :type key: str

        :param value: The key's value.
        :type value: str or int

        :param pair: Optional key/value pair. Example: name="James"
        :type pair: key/value pair

        :rtype: bulbs.neo4jserver.client.Neo4jResponse

        """
        key, value = self._get_key_value(key, value, pair)
        remove = self._get_method(vertex="remove_vertex", edge="remove_edge")
        return remove(self.index_name,_id,key,value)

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
        key, value = self._get_key_value(key,value,pair)
        script = self.client.scripts.get('index_count')
        params = dict(index_name=self.index_name,key=key,value=value)
        resp = self.client.gremlin(script,params)
        total_size = int(resp.content)
        return total_size

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


class ExactIndex(Index):
    """
    Neo4j's Lucence exact index.

    :cvar index_type: Index type.
    :cvar index_provider: Index provider.
    :cvar blueprints_type: Blueprints type.

    :ivar client: Neo4jClient object 
    :ivar result: Neo4jResult object.

    """
    index_type = "exact"
    index_provider = "lucene"
    blueprints_type = "MANUAL"

    def query(self, key, query_string):
        """
        Return all the elements in the index matching the query.

        :param key: The index key. 
        :type key: str

        :param query_string: The query string. Example: "Jam*".
        :type value: str or int

        :rtype: Element generator

        """
        # TODO: Maybe update this to use the REST endpoint.
        script = self.client.scripts.get('query_exact_index')
        params = dict(index_name=self.index_name, key=key, query_string=query_string)
        resp = self.client.gremlin(script, params)
        return initialize_elements(self.client, resp)       

# TODO: add fulltext index tests
class FulltextIndex(Index):
    """
    Neo4j's Lucence fulltext index.

    :cvar index_type: Index type.
    :cvar index_provider: Index provider.
    :cvar blueprints_type: Blueprints type.

    :ivar client: Neo4jClient object 
    :ivar result: Neo4jResult object.
    
    """
    index_type = "fulltext"
    index_provider = "lucene"
    blueprints_type = "MANUAL"

    def query(self, query_string):
        """
        Return elements mathing the query.

        See http://lucene.apache.org/core/3_6_0/queryparsersyntax.html

        :param query_string: The query formatted in the Lucene query language. 
        :type query_string: str

        :rtype: Element generator

        """
        query = self._get_method(vertex="query_vertex", edge="query_edge")
        resp = query(self.index_name, query_string)
        return initialize_elements(self.client,resp)



# Uncdocumented -- experimental
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


# Uncdocumented -- experimental -- use put_unique and get_unique for now
class UniqueIndex(ExactIndex):
    pass

