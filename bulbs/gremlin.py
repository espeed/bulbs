# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
An interface for executing Gremlin scripts on the resource.

"""
from utils import initialize_elements, get_one_result


class Gremlin(object):
    """
    An interface for executing Gremlin scripts on the resource.
    
    :param resource: The Resource object for the database.
    :type resource: Resource

    .. note:: To get the raw query results, use the lower-level method 
              self.resource.gremlin(script, params)
           
              Use case: You are returning element IDs and the actual
              elements are cached in Redis or Membase.

    """

    def __init__(self,resource):
        self.resource = resource

    def command(self,script,params=None):
        """
        Returns raw results of an arbitrary Gremlin command.

        :param script: Gremlin script to execute on the resource.
        :type script: str
 
        :param params: Optional paramaters to bind to the Gremlin script. 
        :type params: dict or None

        """

        resp = self.resource.gremlin(script,params)
        return get_one_result(resp)
        
    def query(self,script,params=None):
        """
        Returns initialized results of an arbitrary Gremlin query.

        :param script: Gremlin script to execute on the resource.
        :type script: str
 
        :param params: Optional paramaters to bind to the Gremlin script. 
        :type params: dict or None

        """

        resp = self.resource.gremlin(script,params)
        return initialize_elements(self.resource,resp)
 
