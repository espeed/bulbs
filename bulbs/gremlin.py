# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
An interface for executing Gremlin scripts on the resource.

"""
from utils import initialize_elements

class Gremlin(object):
    """An interface for executing Gremlin scripts on the resource."""

    def __init__(self,resource):
        self.resource = resource

    def query(self,script,params,**kwds):
        """
        Returns initialized results of an arbitrary Gremlin scripts
        run on the resource.

        :param script: Gremlin script to send to the resource.
        :param kwds: Resource-specific keyword params.

        """
        resp = self.resource.gremlin(script,params,**kwds)
        return initialize_elements(self.resource,resp)
 
    def execute(self,script,params,**kwds):
        """
        Returns raw results of an arbitrary Gremlin script.

        :param script: Gremlin script to send to the resource. 
        :param kwds: Resource-specific keyword params.

        """
        resp = self.resource.gremlin(script,params,**kwds)
        return list(resp.results)


