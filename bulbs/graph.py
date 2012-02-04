# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
from bulbs.config import Config
from bulbs.factory import Factory
from bulbs.resource import Resource
from bulbs.element import Vertex, Edge
from bulbs.model import Relationship
from bulbs.index import Index


class Graph(object):
    """Abstract base class for the resource Graph implementataions."""
    
    default_uri = None
    default_index = Index
    resource_class = Resource

    def __init__(self, root_uri=None):
        root_uri = self.get_root_uri(root_uri)

        self.config = Config(root_uri)
        self.resource = self.resource_class(self.config)
        self.factory = Factory(self.resource)

        self.vertices = self.build_proxy(Vertex)
        self.edges = self.build_proxy(Edge)

        #self.relationships = self.build_proxy(Relationship)

    def get_root_uri(self, root_uri):
        if not root_uri:
            root_uri = self.default_uri
        return root_uri

    def add_proxy(self, proxy_name, element_class, index_class=None):
        """Adds an element proxy to an existing Graph object."""
        proxy = self.build_proxy(element_class, index_class)
        setattr(self, proxy_name, proxy)
    
    def build_proxy(self, element_class, index_class=None):
        """Returns an element proxy built to specifications."""
        if not index_class:
            index_class = self.default_index
        return self.factory.build_element_proxy(element_class, index_class)

    def load_graphml(self,uri):
        """Loads a GraphML file into the database and returns the response."""
        raise NotImplementedError
        
    def save_graphml(self):
        """Returns a GraphML file representing the entire database."""
        raise NotImplementedError

    def clear(self):
        """Deletes all the elements in the graph.

        .. admonition:: WARNING 

           This will delete all your data!

        """
        raise NotImplementedError
