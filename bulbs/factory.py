# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Build instances used to interact with the backend resources.

"""

class Factory(object):

    def __init__(self, resource):
        self.resource = resource

    def build_model(self, element_class, index, kwds):
        """Returns an instantiated Model with keyword attributes set."""
        model = element_class(resource)
        model._set_keyword_attributes(kwds)
        model._index = index
        return model

    def build_element(resource,result):
        # result should be a single Result object, not a list or generator
        element_class = get_element_class(resource,result)
        element = element_class(resource)
        element._initialize(result)
        return element

    def build_element_proxy(self, element_class, index_class, index_name=None):
        proxy_class = element_class.get_proxy_class()
        element_proxy = proxy_class(element_class, self.resource)
        primary_index = self.get_index(element_class,index_class,index_name)
        element_proxy.index = primary_index
        return element_proxy

    def build_index_proxy(self, element_class, index_class):
        base_type = element_class.get_base_type()
        proxy_class = index_class.get_proxy_class(base_type)
        index_proxy = proxy_class(index_class, self.resource)
        return index_proxy

    def get_index(self, element_class, index_class, index_name=None):
        if index_name is None:
            index_name = element_class.get_index_name(self.resource.config)
        index_proxy = self.build_index_proxy(element_class, index_class)
        index = index_proxy.get_or_create(index_name)
        return index

    

