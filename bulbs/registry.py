# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
from bulbs.element import Vertex, Edge


class Registry(object):
    """
    Store runtime configuration settings.

    :param config: Config object.
    :type config: bulbs.config.Config

    """
    
    def __init__(self, config):
        self.config = config
        self.class_map = dict(vertex=Vertex,edge=Edge)
        self.proxy_map = dict()
        self.index_map = dict()
        self.scripts_map = dict()

    # Classes

    def add_class(self, element_class):
        """
        Adds an element class to the registry.

        :param element_class: Element class.
        :type element_class: class

        :rtype: None

        """
        # Vertex and Edge are always set by default
        if element_class not in (Vertex, Edge): 
            # TODO: may get into an issue with name clashes
            # a vertex has the same element_type as an edge's label;
            # for now "don't do that".
            element_key = element_class.get_element_key(self.config)
            self.class_map[element_key] = element_class

    def get_class(self, element_key):
        """
        Returns the element class given the element key.

        :param element_key: Element key, value of element_type or label.
        :type element_key: str

        :rtype: class

        """
        return self.class_map.get(element_key)

    # Proxies

    def add_proxy(self, name, proxy):
        """
        Adds a proxy object to the registry.

        :param name: Proxy name.
        :type name: str

        :param proxy: Proxy object.
        :type proxy: object

        :rtype: None

        """
        self.proxy_map[name] = proxy

    def get_proxy(self, name):
        """
        Returns proxy objects given the name.

        :param name: Proxy name.
        :type name: str

        :rtype: class

        """
        return self.proxy_map[name]

    # Indices

    def add_index(self, index_name, index):
        """
        Adds an index object to the registry.

        :param name: Index name.
        :type name: str

        :param name: index
        :type name: Index

        :rtype: None

        """
        self.index_map[index_name] = index
        
    def get_index(self, index_name):
        """
        Returns the Index object for the given index name.

        :param index_name: Index name.
        :type index_name: str

        :rtype: Index

        """
        return self.index_map[index_name]
 
    # Scripts

    def add_scripts(self, name, scripts):
        """
        Adds a scripts object to the registry.

        :param name: Scripts object name.
        :type name: str

        :param name: Scripts object.
        :type name: Scripts

        :rtype: None

        """
        self.scripts_map[name] = scripts

    def get_scripts(self, key):
        """
        Returns a scripts object for the given name.

        :param name: Scripts object name.
        :type name: str

        :rtype: Scripts

        """
        return self.scripts_map[key]

