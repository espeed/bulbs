# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
import unittest

from bulbs.config import Config, DEBUG, ERROR
from bulbs.element import Vertex, VertexProxy, Edge, EdgeProxy       
from .testcase import BulbsTestCase


class IndexTestCase(BulbsTestCase):
    
    def setUp(self):
        self.indicesV = self.vertex_index_proxy(self.index_class,self.client)
        self.indicesE = self.edge_index_proxy(self.index_class,self.client)

        self.indicesV.delete("test_idxV")
        self.indicesE.delete("test_idxE")
        
        self.vertices = VertexProxy(Vertex,self.client)
        self.vertices.index = self.indicesV.get_or_create("test_idxV")

        self.edges = EdgeProxy(Edge,self.client)
        self.edges.index = self.indicesE.get_or_create("test_idxE")
               
    def test_index(self):
        index_name = "test_idxV"
        # need to fix this to accept actual data types in POST
        ikeys = '[name,location]'
        james = self.vertices.create({'name':'James'})
        self.vertices.index.put(james._id,'name','James')
        self.vertices.index.put(james._id,'location','Dallas')
        results = self.vertices.index.lookup('name','James')
        results = list(results)
        assert len(results) == 1
        assert results[0].name == "James"
        
        total_size = self.vertices.index.count('name','James')
        assert total_size == 1
        i2 = self.indicesV.get(index_name)
        assert self.vertices.index.index_name == i2.index_name
        
        self.vertices.index.remove(james._id,'name','James')
        james = self.vertices.index.get_unique('name','James')
        assert james is None
  
        self.indicesV.delete(index_name)

