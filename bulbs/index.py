# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
An interface for interacting with indices on Rexster.

"""

from element import Vertex, Edge
from gremlin import Gremlin
from config import TYPE_VAR

class Index(object):
    """
    Creates, retrieves, and deletes indices provided by the graph database.

    Use this class to get, put, and update items in an index.
    

    :param resource: The Resource object for the database.

    :param results: The results list returned by Rexster.

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

    def __init__(self,resource,results,*classes):
        """
        Initializes the Index object.
        """
        self.resource = resource
        self._results = results
        self._classes = classes
        self._class_map = dict(vertex=Vertex,edge=Edge)
        self._update_class_map(classes)

    @property
    def index_name(self):
        """Returns the index name."""
        return self._results['name']

    @property
    def index_class(self):
        """Returns the index class, which will either be vertex or edge."""
        return self._results['class']
        # Temp hack until we fix Rexster so it doesn't return the full Java 
        # WE don't need this anymore. Stephen fixed the Rexster bug! :)
        # class
        #return self._get_index_class(index_class)

    @property
    def index_type(self):
        """Returns the index type, which will either be automatic or manual."""
        return self._results['type']
    
    def put(self,_id,key=None,value=None,**pair):
        """
        Put an element into the index at key/value and return Rexster's 
        response.

        :param _id: The element ID.

        :param key: The index key. This is optional because you can instead 
                    supply a key/value pair such as name="James". 

        :param value: The index key's value. This is optional because you can 
                      instead supply a key/value pair such as name="James". 

        :param **pair: Optional keyword param. Instead of supplying key=name 
                       and value = 'James', you can supply a key/value pair in
                       the form of name='James'.

        """
        # NOTE: if you ever change the _id arg to element, change remove() too
        if pair:
            key, value = pair.popitem()
        target = "%s/%s" % (self._base_target(), self.index_name)
        params = {'key':key,'value':value,'class':self.index_class,'id':_id}
        resp = self.resource.post(target,params)
        return resp

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

        :param **pair: Optional keyword param. Instead of supplying key=name 
                       and value = 'James', you can supply a key/value pair in 
                       the form of name='James'.

        """
        for result in self.get(key,value,**pair):
            self.remove(result._id,key,value,**pair)
        resp = self.put(_id,key,value,**pair)
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

        :param **pair: Optional keyword param. Instead of supplying key=name 
                       and value = 'James', you can supply a key/value pair in
                       the form of name='James'.
        """
        return self.put_unique(_id,key,value,**pair)

    def get(self,key=None,value=None,raw=False,**pair):
        """
        Return a generator containing all the elements with key property equal 
        to value in the index.

        :param key: The index key. This is optional because you can instead 
                    supply a key/value pair such as name="James". 

        :param value: The index key's value. This is optional because you can 
                      instead supply a key/value pair such as name="James". 

        :param raw: Optional keyword param. If set to True, it won't try to 
                    initialize the results. Defaults to False. 

        :param **pair: Optional keyword param. Instead of supplying key=name 
                       and value = 'James', you can supply a key/value pair in
                       the form of name='James'.
        """
        if pair:
            key, value = pair.popitem()
        target = "%s/%s" % (self._base_target(),self.index_name)
        params = dict(key=key,value=value)
        resp = self.resource.get(target,params)
        for result in resp.results:
            yield self._initialize_result(result,raw)
         
    def get_unique(self,key=None,value=None,raw=False,**pair):
        """
        Returns a max of 1 elements matching the key/value pair in the index.

        :param key: The index key. This is optional because you can instead 
                    supply a key/value pair such as name="James". 

        :param value: The index key's value. This is optional because you can 
                      instead supply a key/value pair such as name="James". 

        :param raw: Optional keyword param. If set to True, it won't try to 
                    initialize the results. Defaults to False. 

        :param **pair: Optional keyword param. Instead of supplying key=name 
                       and value = 'James', you can supply a key/value pair in
                       the form of name='James'.
        """

        generator = self.get(key,value,raw,**pair)
        results = list(generator)
        if len(results) > 1:
            raise("Unique index result contains more than one item.")
        if results:
            return results[0]

    def count(self,key=None,value=None,**pair):
        """
        Return a count of all elements with 'key' equal to 'value' in the index.

        :param key: The index key. This is optional because you can instead 
                    supply a key/value pair such as name="James". 

        :param value: The index key's value. This is optional because you can 
                      instead supply a key/value pair such as name="James". 

        :param **pair: Optional keyword param. Instead of supplying key=name 
                       and value = 'James', you can supply a key/value pair in
                       the form of name='James'.
        """
        if pair:
            key, value = pair.popitem()
        target = "%s/%s/count" % (self._base_target(),self.index_name)
        params = dict(key=key,value=value)
        resp = self.resource.get(target,params)
        return resp.total_size
     
    def keys(self):
        """Return the index's keys."""
        target = "%s/%s/keys" % (self._base_target(),self.index_name)
        resp = self.resource.get(target,params=None)
        return list(resp.results)

    def remove(self,_id,key=None,value=None,**pair):
        """
        Remove the element from the index located by key/value.

        :param _id: The element ID.

        :param key: The index key. This is optional because you can instead 
                    supply a key/value pair such as name="James". 

        :param value: The index key's value. This is optional because you can 
                      instead supply a key/value pair such as name="James". 

        :param **pair: Optional keyword param. Instead of supplying key=name 
                       and value = 'James', you can supply a key/value pair in
                       the form of name='James'.
        """

        if pair:
            key, value = pair.popitem()
        target = "%s/%s" % (self._base_target(),self.index_name)
        params = {'key':key,'value':value,'class':self.index_class,'id':_id}
        resp = self.resource.delete(target,params)
        return resp

    def rebuild(self,raw=False):
        # need class_map b/c the Blueprints need capitalized class names, 
        # but Rexster returns lower-case class names for index_class
        class_map = dict(vertex='Vertex',edge='Edge')
        klass = class_map[self.index_class]
        script = "index = g.getIndex('%s',%s);" % (self.index_name,klass)
        script = script + "AutomaticIndexHelper.reIndexElements(g, index, g.getVertices())"
        resp = Gremlin(self.resource).execute(script,raw=True)
        if raw or not resp.results:
            return resp
        return list(resp.results)

    def _get_index_class(self,index_class):
        """
        Returns the index class. This is a hack that can go away when Rexster
        bug is fixed.

        :param index_class: The index class returned by Rexster. Example: 
                            "class":"com.tinkerpop.blueprints.pgm.Vertex"
        """

        if "Vertex" in index_class:
            index_class = "vertex"
        elif "Edge" in index_class:
            index_class = "edge"
        else:
            raise Exception("Invalid index class")
        return index_class

    def _update_class_map(self,classes):
        """
        Adds a list of element classes to the class_map.

        :param classes: A list of element classes to add to the class_map.
        """
        for element_class in classes:
            self._add_element_class(element_class)
            
    def _base_target(self):
        """Returns the base URL for the indices resource on Rexster.""" 
        base_target = "%s/indices" % (self.resource.db_name)
        return base_target

    ################ 3 similar methods are in gremlin.Gremlin() #########
    def _initialize_result(self,result,raw):
        """
        Maybe initialize the object returned in the query result.

        If the element's class was passed in to the query method and raw is 
        False, it will initialize the element. If raw is True, it won't try to 
        initialize the element and will just return the raw result.

        :param result: An individual result item returned by Rexster (not a 
                       result list).

        :param raw: Optional keyword param. If set to True, it won't try to 
                    initialize data. Defaults to False. 

        """
        if raw is False:
            element_class = self._get_element_class(result)
            if element_class:
                result = element_class(self.resource,result)
        return result

    def _add_element_class(self,element_class):
        """Ad an individual element class to the class map."""
        element_type = getattr(element_class,TYPE_VAR,None)
        if element_type:
            self._class_map[element_type] = element_class

    def _get_element_class(self,result):
        """
        Return the element class for a query result item.

        :param result: An individual result item returned by Rexster (not a  
                       result list).

        """
        if len(self._classes) == 1:
            # if you pass in just one class, we assume you know what you're 
            # doing and you are saying that all of the results will be of the 
            # class you specified, even though the results don't have an 
            # element_type property saved in the DB
            # TODO: Maybe upgrade the Gremlin method to behave the same way.
            element_class = self._classes[0]
        else:
            element_type = result.get(TYPE_VAR,None)
            if element_type not in self._class_map:  
                # just return a generic Vertex/Edge class
                element_type = result['_type']
            element_class = self._class_map.get(element_type,None) 
        return element_class
    ##########################################################################


class IndexProxy(object):
    """
    An interface for interacting with indices on Rexster.

    :param resource: The Resource object for the database.

    :param classes: Zero or more subclasses of Element to use when 
                    initializing the the elements returned by the query. 
                    For example, if Person is a subclass of Node (which 
                    is defined in model.py and is a subclass of Vertex), 
                    and the query returns person elements, pass in the 
                    Person class and the method will use the element_type
                    defined in the class to initialize the returned items
                    to a Person object.
    """
    
    def __init__(self,resource,*classes):
        """
        Initialize the Gremlin proxy object.

        """

        self.resource = resource
        self._classes = classes
                        
    def create(self,index_name,index_class,index_type,index_keys=None):
        """ 
        Adds an index to the database and returns it. 

        index_keys must be a string in this format: '[k1,k2]'
        Don't pass actual list b/c keys get double quoted.

        :param index_name: The name of the index to create.

        :param index_class: The class of the elements stored in the index. 
                            Either vertex or edge.
        
        """
        target = "%s/%s" % (self._base_target(), index_name)
        params = {'class':index_class,'type':index_type}
        if index_keys: 
            params.update({'keys':index_keys})
        resp = self.resource.post(target,params)
        return Index(self.resource,resp.results,*self._classes)
        
    def get(self,index_name):
        """
        Returns the Index object with the specified name.

        :param index_name: The name of the index.

        """
        target = "%s/%s" % (self._base_target(), index_name)
        resp = self.resource.get(target,params=None)
        # NOTE: Get returns the index properties as part of content,
        # not results. I've filed a bug report. Stephen fixed it :)
        #results = {'name':resp.index_name,
        #           'type':resp.index_type,
        #           'class':resp.index_class}
        return Index(self.resource,resp.results,*self._classes)

    def delete(self,name):
        """
        Deletes/drops an index and returns the Rexster Response object.

        :param name: The name of the index.

        """
        target = "%s/%s" % (self._base_target(),name)
        resp = self.resource.delete(target,params=None)
        return resp

    def _base_target(self):
        """Returns the base URL target for the indices resource on Rexster."""
        base_target = "%s/indices" % (self.resource.db_name)
        return base_target
