# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
An interface for executing Gremlin scripts on Rexster.

"""
import simplejson as json
from config import TYPE_VAR


class Gremlin(object):
    """An interface for executing Gremlin scripts on Rexster."""

    def __init__(self,resource):
        """
        Initialize the Gremlin proxy object.
        
        :param resource: The Resource object for the database.

        """
        self.resource = resource
        self.base_target = "%s/tp/gremlin" % (self.resource.db_name)
        self.class_map = {}


    def query(self,script,*classes,**kwds):
        """
        Returns initialized results of arbitrary Gremlin scripts run through Rexster.

        :param script: Gremlin script to send to Rexster. Since this begins 
                       from the context of a graph instead of an element, the 
                       script should begin with the reference to itself 
                       (g) instead of a reference to the element (v or e). 
                       Example:

                       .. code-block:: groovy

                          // do this... 
                          g.v(1).outE('created') 
                           
                          // instead of... 
                          v.outE('created')

        :param classes: Zero or more subclasses of Element to use when 
                        initializing the the elements returned by the query. 
                        For example, if Person is a subclass of Node (which 
                        is defined in model.py and is a subclass of Vertex), 
                        and the query returns person elements, pass in the 
                        Person class and the method will use the element_type
                        defined in the class to initialize the returned items
                        to a Person object.

        :param return_keys: Optional keyword param. A comman-separated list of
                            keys (DB properties) to return. If set to None, it
                            returns all properties. Defaults to None.

        :param raw: Optional keyword param. If set to True, it won't try to 
                    initialize data. Defaults to False. 
        
        """
        raw = kwds.pop('raw',False)
        resp = self._query(script,*classes,**kwds)
        for result in resp.results:
            yield self._initialize_result(result,raw)
 

    def execute(self,script,**kwds):
        """
        Returns raw results of arbitrary Gremlin scripts run through Rexster.

        :param script: Gremlin script to send to Rexster. Since this begins 
                       from the context of a graph instead of an element, the 
                       script should begin with the reference to itself 
                       (g) instead of a reference to the element (v or e). 
                       Example:

                       .. code-block:: groovy

                          // do this... 
                          g.v(1).outE('created') 
                           
                          // instead of... 
                          v.outE('created')

        :param return_keys: Optional keyword param. A comman-separated list of
                            keys (DB properties) to return. If set to None, it
                            returns all properties. Defaults to None.

        :param raw: Optional keyword param. If set to True, it won't try to 
                    initialize data. Defaults to False. 
        
        """
        raw = kwds.pop('raw',False)
        classes = ()
        resp = self._query(script,*classes,**kwds)
        if raw:
            return resp
        return list(resp.results)


    def lds_query(self,script,raw=False):
        """Return queries on remote LinkedData stores."""
        # this hack will go away when the LinkedDataSail mods to Rexster are finished. 
        lds_hack = "g = new LinkedDataSailGraph(new MemoryStoreSailGraph());"
        script = lds_hack + self._trim_lines(script)
        params = dict(script=script)
        resp = self.resource.get(self.base_target,params)
        for result in resp.results:
            yield self._initialize_result(result,raw)

    def _query(self,script,*classes,**kwds):
        """Returns raw results of arbitrary Gremlin scripts run through Rexster."""
        #script = self._trim_lines(script)
        # do these imports here to avoid circular dependency issue with element.py
        from element import Vertex, Edge
        default_class_map = dict(vertex=Vertex,edge=Edge)
        self.class_map.update(default_class_map)
        self._add_classes(classes)
        return_keys = kwds.pop('return_keys',None)
        params = dict(script=script)
        if return_keys:
            params.update(return_keys=return_keys)
        resp = self.resource.get(self.base_target,params)
        return resp

    def _element_query(self,element,script,*classes,**kwds):
        """
        This is called by Element and probably won't be useful anywhere else.

        Returns a generator containing the results of the Gremlin script. 
        Remember you can always use the list() function to turn an iterator or 
        a generator into a list. Sometimes it's useful to turn a generator into
        a list when doing unittests or when you want to check how many items 
        are in the results. For example::
            
            results = person.gremlin('v.outE.inV')
            results = list(results)
            
        :param script: Gremlin script to send to Rexster. Since this begins 
                       from the context of an element instead of a graph, the 
                       script should begin with the reference to itself 
                       (v or e) instead of a reference to the graph (g). 
                       Example:

                       .. code-block:: groovy

                       // do this... 
                       v.outE('created') 
                        
                       // instead of... 
                       g.v(1).outE('created')

        :param classes: Zero or more subclasses of Element to use when 
                        initializing the the elements returned by the query. 
                        For example, if Person is a subclass of Node (which 
                        is defined in model.py and is a subclass of Vertex), 
                        and the query returns person elements, pass in the 
                        Person class and the method will use the element_type
                        defined in the class to initialize the returned items
                        to a Person object.

        :param kwds: name/value pairs of optional arguments:
                        
        :param return_keys: Optional keyword param. A comman-separated list of
                            keys (DB properties) to return. If set to None, it
                            returns all properties. Defaults to None.

        :param raw: Optional keyword param. If set to True, it won't try to 
                    initialize data. Defaults to False. 

        """
        script = self._trim_lines(script)
        default_class_map = kwds.pop('default_class_map')
        self.class_map.update(default_class_map)
        return_keys = kwds.pop('return_keys',None)
        raw = kwds.pop('raw',False)
        self._add_classes(classes)
        #path = element.path()
        target = "%s/%s/tp/gremlin" % (element._base_target(),element._id)
        params = dict(script=script)
        if return_keys:
            params.update(return_keys=return_keys)
        print "TARGET", target
        resp = self.resource.get(target,params)
        for result in resp.results:
            yield self._initialize_result(result,raw)

    def _trim_lines(self,script):
        """
        Returns a clean Gremlin script, trimmed of its whitespace and 
        ready to be sent Rexster.

        :param script: The Gremlin script you want to clean up.

        """ 
        lines = []
        for line in script.split('\n'):
            line = line.strip()
            if line:
                lines.append(line)
        script = ";".join(lines)
        return script
        
    def _initialize_result(self,result,raw):
        """
        Maybe initialize the object returned in the query result.

        If the element's class was passed in to the query method and raw is False, 
        it will initialize the element. If raw is True, it won't try to initialize
        the element and will just return the raw result.

        :param result: An individual result item returned by Rexster (not a result list).

        :param raw: Optional keyword param. If set to True, it won't try to 
                    initialize data. Defaults to False. 

        """
        if raw is False:
            element_class = self._get_element_class(result)
            if element_class:
                result = element_class(self.resource,result)
        return result
       
    def _add_classes(self,classes):
        """Add a list of element classes to the class_map."""
        for element_class in classes:
            self._add_element_class(element_class)   
 
    def _add_element_class(self,element_class):
        """Ad an individual element class to the class map."""
        element_type = getattr(element_class,TYPE_VAR,None)
        if element_type:
            self.class_map[element_type] = element_class

    def _get_element_class(self,result):
        """
        Return the element class for a query result item.

        :param result: An individual result item returned by Rexster (not a result list).

        """
        element_type = result.get(TYPE_VAR,None)
        if element_type not in self.class_map:
            element_type = result['_type']
        return self.class_map.get(element_type,None)
 
