# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
import unittest

from bulbs.tests.testcase import BulbsTestCase
from bulbs.element import Vertex, VertexProxy, Edge       
from bulbs.index import IndexProxy

class IndexTestCase(BulbsTestCase):
    
    def setUp(self):
        self.vertices = VertexProxy(Vertex,self.resource)
        self.indices = IndexProxy(self.index_class,self.resource)
       
    def test_index(self):
        index_name = "TEST"
        # need to fix this to accept actual data types in POST
        ikeys = '[name,location]'
        self.indices.delete(index_name)
        i1 = self.indices.create(index_name,Vertex)
        assert i1.index_name == index_name
        assert i1.index_type == "automatic"
        james = self.vertices.create({'name':'James'})
        i1.put(james._id,'name','James')
        i1.put(james._id,'location','Dallas')
        results = i1.get('name','James')
        results = list(results)
        print "RESULTS", results
        assert len(results) == 1
        assert results[0].name == "James"
        total_size = i1.count('name','James')
        assert total_size == 1
        # NOTE: only automatic indices have user provided keys
        #keys = i1.keys()
        #assert 'name' in keys
        #assert 'location' in keys
        i2 = self.indices.get(index_name,Vertex)
        print "INDEX_NAME", index_name, i1.index_name, i2.index_name
        assert i1.index_name == i2.index_name
        
        # remove vertex is bugged
        #i1.remove(james._id,'name','James')
        #james = i1.get_unique('name','James')
        #assert james is None
  
        # only can rebuild automatic indices
        i3 = self.indices.get("vertices",Vertex)
        results = i3.rebuild()
        assert type(results) == list

        self.indices.delete(index_name)

        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IndexTestCase))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

