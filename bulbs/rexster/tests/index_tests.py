# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
import unittest

from bulbs.tests.testcase import BulbsTestCase
from bulbs.element import Vertex, VertexProxy, Edge, EdgeProxy
from bulbs.config import Config
    
from bulbs.rexster import RexsterClient, REXSTER_URI
from bulbs.rexster.index import VertexIndexProxy, EdgeIndexProxy, ManualIndex

config = Config(REXSTER_URI)
BulbsTestCase.client = RexsterClient(config)
BulbsTestCase.index_class = ManualIndex

 
class IndexTestCase(BulbsTestCase):
    
    def setUp(self):
        self.indicesV = VertexIndexProxy(self.index_class,self.client)
        self.indicesE = EdgeIndexProxy(self.index_class,self.client)

        self.indicesV.delete("test_idxV")
        self.indicesE.delete("test_idxE")

        self.vertices = VertexProxy(Vertex,self.client)
        self.vertices.index = self.indicesV.get_or_create("test_idxV")

        self.edges = EdgeProxy(Edge,self.client)
        self.edges.index = self.indicesE.get_or_create("test_idxE")

    def test_index(self):
        index_name = "test_idxV"
        # need to fix this to accept actual data types in POST
        #ikeys = '[name,location]'
        #self.indices.delete(index_name)
        #i1 = self.indices.create(index_name,Vertex)
        #assert i1.index_name == index_name
        #assert i1.index_type == "automatic"

        james = self.vertices.create({'name':'James'})
        self.vertices.index.put(james._id,'name','James')
        self.vertices.index.put(james._id,'location','Dallas')
        results = self.vertices.index.lookup('name','James')
        results = list(results)
        #print "RESULTS", results
        assert len(results) == 1
        assert results[0].name == "James"
        total_size = self.vertices.index.count('name','James')
        assert total_size == 1
        # NOTE: only automatic indices have user provided keys
        #keys = self.vertices.index..keys()
        #assert 'name' in keys
        #assert 'location' in keys
        i2 = self.indicesV.get(index_name)
        #print "INDEX_NAME", index_name, self.vertices.index..index_name, i2.index_name
        assert self.vertices.index.index_name == i2.index_name
        
        # remove vertex is bugged
        #self.vertices.index..remove(james._id,'name','James')
        #james = self.vertices.index..get_unique('name','James')
        #assert james is None
  
        # only can rebuild automatic indices
        #i3 = self.indices.get("vertices",Vertex)
        #results = i3.rebuild()
        #assert type(results) == list

        self.indicesV.delete(index_name)

        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IndexTestCase))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

