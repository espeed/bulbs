import unittest
from bulbs.config import Config
from bulbs.tests.resource_tests import ResourceTestCase
from bulbs.rexster.resource import RexsterResource, REXSTER_URI

import time

class RexsterResourceTestCase(ResourceTestCase):

    def setUp(self):
        config = Config(REXSTER_URI)
        self.resource = RexsterResource(config)

class RexsterIndexTestCase(unittest.TestCase):

    def setUp(self):
        config = Config(REXSTER_URI)
        self.resource = RexsterResource(config)

    #
    # Index Controller Tests
    #

    def test_create_vertex_index(self):
        name = "test_idxV"
        self.resource.delete_vertex_index(name)
        resp = self.resource.create_vertex_index(name)
        assert resp.results.get("name") == name
        assert resp.results.get("class") == "vertex"  
        assert resp.results.get("type") == "manual"
        
    def test_get_all_indices(self):
        resp = self.resource.get_all_indices()
        assert resp.total_size > 1
        # the only indices created by default are automatic 
        # so it should be true for whatever index is listed first in the results
        # not true anymore! -- now the default indices are manual
        #assert resp.results.next().get('type') == "manual"

    def test_get_index(self):
        name = "test_idxV"
        self.resource.delete_index(name)
        self.resource.create_vertex_index(name)
        resp = self.resource.get_index(name)
        assert resp.results.get("name") == name
        assert resp.results.get("class") == "vertex"  
        assert resp.results.get("type") == "manual"
                
    def test_delete_index(self):
        name = "test_idxV"
        resp = self.resource.delete_index(name)
    
    #
    # Index Container Tests
    #

    def test_put_and_lookup_vertex(self):
        index_name = "test_idxV"
        self.resource.delete_index(index_name)
        self.resource.create_vertex_index(index_name)
        respV = self.resource.create_vertex({'name':'James'})
        key, value, _id = "name", "James", respV.results.get_id()
        self.resource.put_vertex(index_name,key,value,_id)
        resp = self.resource.lookup_vertex(index_name,key,value)
        assert resp.total_size == 1
        assert resp.results.next().get("name") == "James"
        
    def test_remove_vertex(self):
        name = "test_idxV"
        self.resource.delete_index(name)
        self.resource.create_vertex_index(name)
        respV = self.resource.create_vertex({'name':'James'})
        key, value = "name", "James"
        self.resource.put_vertex(name,key,value,respV.results.get_id())
        print "HERE", respV.raw
        self.resource.remove_vertex(name,respV.results.get_id(),key,value)
        resp = self.resource.lookup_vertex(name,key,value)
        assert resp.total_size == 0
 

class RexsterAutomaticIndexTestCase(unittest.TestCase):
    
    def setUp(self):
        config = Config(REXSTER_URI)
        config.debug = True
        self.resource = RexsterResource(config)

    def test_create_automatic_vertex_index(self):
        index_name = "test_automatic_idxV"
        element_class = "TestVertex"
        self.resource.delete_index(index_name)
        resp = self.resource.create_automatic_vertex_index(index_name,element_class)
        print "RAW", resp.raw

    def test_create_automatic_indexed_vertex(self):
        index_name = "test_automatic_idxV"
        timestamp = int(time.time())
        timestamp = 12345
        data = dict(name="James",age=34,timestamp=timestamp)
        resp = self.resource.create_indexed_vertex_automatic(data,index_name)
        #print resp.raw
        resp = self.resource.lookup_vertex(index_name,"timestamp",timestamp)
        print "RAW2", resp.raw



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RexsterResourceTestCase))
    suite.addTest(unittest.makeSuite(RexsterIndexTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
