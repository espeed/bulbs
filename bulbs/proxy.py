# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
"""
Build proxy instances used to interact with the backend resources.

"""

class ProxyFactory(object):

    def __init__(self, resource, index_proxies):
        self.resource = resource
        #self.element_proxies = element_proxies
        self.index_proxies = index_proxies

    def build_element_proxy(self, element_class, index_class, index_name=None):
        proxy_class = element_class.get_proxy_class()
        element_proxy = proxy_class(element_class, self.resource)
        primary_index = self.get_primary_index(element_class,index_class,index_name)
        element_proxy.index = primary_index
        return element_proxy

    def build_index_proxy(self, element_class, index_class):
        index_proxy_class = self.index_proxies.get(element_class._class_type)
        index_proxy = index_proxy_class(index_class, self.resource)
        return index_proxy

    def get_primary_index(self, element_class, index_class, index_name=None):
        if index_name is None:
            index_name = element_class.get_index_name(self.resource.config)
        index_proxy = self.build_index_proxy(element_class, index_class)
        primary_index = index_proxy.get_or_create(index_name)
        return primary_index

    

