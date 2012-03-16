import sys
import argparse

import unittest
from bulbs.config import Config
from bulbs.tests.client_tests import ClientTestCase
from bulbs.rexster.client import RexsterClient, REXSTER_URI

import time

# Default database. You can override this with the command line:
# $ python client_tests.py --db mydb
db_name = "tinkergraph"

class RexsterClientTestCase(ClientTestCase):

    def setUp(self):
        self.client = RexsterClient(db_name=db_name)

# The index test cases have been moved to the Bulbs ClientTestCAset

class RexsterIndexTestCase(unittest.TestCase):

    def setUp(self):
        self.client = RexsterClient(db_name=db_name)

    def _delete_vertex_index(self,index_name):
        try:
            self.client.delete_vertex_index(index_name)
        except LookupError:
            pass


    #
    # Index Controller Tests
    #

    def test_create_vertex_index(self):
        name = "test_idxV"
        self._delete_vertex_index(name)
        resp = self.client.create_vertex_index(name)
        assert resp.results.get("name") == name
        assert resp.results.get("class") == "vertex"  
        assert resp.results.get("type") == "manual"
        
    def test_get_all_indices(self):
        resp = self.client.get_all_indices()
        assert resp.total_size > 1
        # the only indices created by default are automatic 
        # so it should be true for whatever index is listed first in the results
        # not true anymore! -- now the default indices are manual
        #assert resp.results.next().get('type') == "manual"

    def test_get_index(self):
        name = "test_idxV"
        self._delete_vertex_index(name)
        self.client.create_vertex_index(name)
        resp = self.client.get_index(name)
        assert resp.results.get("name") == name
        assert resp.results.get("class") == "vertex"  
        assert resp.results.get("type") == "manual"
                
    def test_delete_index(self):
        name = "test_idxV"
        resp = self._delete_vertex_index(name)
    
    #
    # Index Container Tests
    #

    def test_put_and_lookup_vertex(self):
        index_name = "test_idxV"
        self._delete_vertex_index(index_name)
        self.client.create_vertex_index(index_name)
        respV = self.client.create_vertex({'name':'James'})
        key, value, _id = "name", "James", respV.results.get_id()
        self.client.put_vertex(index_name,key,value,_id)
        resp = self.client.lookup_vertex(index_name,key,value)
        assert resp.total_size == 1
        assert next(resp.results).get("name") == "James"
        
    def test_remove_vertex(self):
        name = "test_idxV"
        self._delete_vertex_index(name)
        self.client.create_vertex_index(name)
        respV = self.client.create_vertex({'name':'James'})
        key, value = "name", "James"
        self.client.put_vertex(name,key,value,respV.results.get_id())
        self.client.remove_vertex(name,respV.results.get_id(),key,value)
        resp = self.client.lookup_vertex(name,key,value)
        assert resp.total_size == 0
 

class RexsterAutomaticIndexTestCase(unittest.TestCase):

    def setUp(self):
        self.client = RexsterClient(db_name=db_name)

    def test_create_automatic_vertex_index(self):
        index_name = "test_automatic_idxV"
        element_class = "TestVertex"
        self._delete_vertex_index(index_name)
        resp = self.client.create_automatic_vertex_index(index_name,element_class)
        

    def test_create_automatic_indexed_vertex(self):
        index_name = "test_automatic_idxV"
        timestamp = int(time.time())
        timestamp = 12345
        data = dict(name="James",age=34,timestamp=timestamp)
        resp = self.client.create_indexed_vertex_automatic(data,index_name)
        resp = self.client.lookup_vertex(index_name,"timestamp",timestamp)

def rexster_client_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RexsterClientTestCase))
    #suite.addTest(unittest.makeSuite(RexsterIndexTestCase))
    return suite

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default=None)
    args = parser.parse_args()
    
    db_name = args.db

    # Now set the sys.argv to the unittest_args (leaving sys.argv[0] alone)
    sys.argv[1:] = []
    
    unittest.main(defaultTest='rexster_client_suite')
