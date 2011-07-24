# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
import unittest

from bulbs.graph import Graph
       
class IndexTestCase(unittest.TestCase):
    
    def test_index(self):
        self.graph = Graph()
        index_name = "TEST"
        # need to fix this to accept actual data types in POST
        ikeys = '[name,location]'
        self.graph.indices.delete(index_name)
        i1 = self.graph.indices.create(index_name,"vertex","automatic",ikeys)
        assert i1.index_name == index_name
        assert i1.index_type == "automatic"
        james = self.graph.vertices.create({'name':'James'})
        i1.put('name','James',james._id)
        i1.put('location','Dallas',james._id)
        results = i1.get('name','James')
        results = list(results)
        assert len(results) == 1
        assert results[0].name == "James"
        total_size = i1.count('name','James')
        assert total_size == 1
        keys = i1.keys()
        assert 'name' in keys
        assert 'location' in keys
        i2 = self.graph.indices.get(index_name)
        print "INDEX_NAME", index_name, i1.index_name, i2.index_name
        assert i1.index_name == i2.index_name
        i1.remove(james._id,'name','James')
        james = i1.get_unique('name','James')
        assert james is None
        results = i1.rebuild()
        assert type(results) == list
        self.graph.indices.delete(index_name)

        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IndexTestCase))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

