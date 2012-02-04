# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
import unittest

from bulbs.config import Config
from bulbs.element import Vertex, VertexProxy, Edge, EdgeProxy       
from bulbs.index import VertexIndexProxy, EdgeIndexProxy, Index
from testcase import BulbsTestCase

class IndexTestCase(BulbsTestCase):
    
    def setUp(self):
        self.indicesV = self.vertex_index_proxy(self.index_class,self.resource)
        self.indicesE = self.edge_index_proxy(self.index_class,self.resource)

        self.indicesV.delete("test_idxV")
        self.indicesE.delete("test_idxE")

        self.vertices = VertexProxy(Vertex,self.resource)
        self.vertices.index = self.indicesV.get_or_create("test_idxV")

        self.edges = EdgeProxy(Edge,self.resource)
        self.edges.index = self.indicesE.get_or_create("test_idxE")
               
    def test_index(self):
        index_name = "test_idxV"
        #index_name = "TEST"
        # need to fix this to accept actual data types in POST
        ikeys = '[name,location]'
        #self.indicesV.delete(index_name)
        #i1 = self.indicesV.create(index_name)
        #assert i1.index_name == index_name
        #assert i1.index_type == "automatic"
        #print self.vertices.index.index_type
        #assert self.vertices.index.index_type == "exact"

        james = self.vertices.create({'name':'James'})
        self.vertices.index.put(james._id,'name','James')
        self.vertices.index.put(james._id,'location','Dallas')
        results = self.vertices.index.lookup('name','James')
        results = list(results)
        #print "RESULTS", results
        assert len(results) == 1
        assert results[0].name == "James"
        total_size = self.vertices.index.count('name','James')
        #print "TOTAL SIZE", total_size
        assert total_size == 1
        # NOTE: only automatic indicesV have user provided keys
        #keys = i1.keys()
        #assert 'name' in keys
        #assert 'location' in keys
        i2 = self.indicesV.get(index_name)
        #print "INDEX_NAME", index_name, self.vertices.index.index_name, i2.index_name
        assert self.vertices.index.index_name == i2.index_name
        
        # remove vertex is bugged
        #i1.remove(james._id,'name','James')
        #james = i1.get_unique('name','James')
        #assert james is None
  
        # only can rebuild automatic indices
        #i3 = self.indicesV.get("vertices")
        #results = i3.rebuild()
        #assert type(results) == list

        self.indicesV.delete(index_name)

