# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
An interface for executing Gremlin scripts on the resource.

"""
from utils import initialize_elements, get_one_result


class Gremlin(object):
    """An interface for executing Gremlin scripts on the resource."""

    def __init__(self,resource):
        self.resource = resource

    def command(self,script,params=None):
        """
        Returns raw results of an arbitrary Gremlin command.

        :param script: Gremlin script to send to the resource. 
        :param params: Paramaters to bind to the Gremlin script. 

        """
        resp = self.resource.gremlin(script,params)
        return get_one_result(resp)
        
    def query(self,script,params=None):
        """
        Returns initialized results of an arbitrary Gremlin query.

        :param script: Gremlin script to send to the resource.
        :param params: Paramaters to bind to the Gremlin script. 

        """
        resp = self.resource.gremlin(script,params)
        return initialize_elements(self.resource,resp)
 
    #
    # NOTE: To get the raw query results, use the lower-level 
    #       self.resource.gremlin(script,params) method.
    #       
    #       Use case: You are returning element IDs and the actual
    #       elements are cached in Redis or Membase.
    #

