import sys
import argparse

import unittest
from bulbs.config import Config
from bulbs.tests.client_tests import ClientTestCase
from bulbs.tests.client_index_tests import ClientIndexTestCase
from bulbs.rexster.client import RexsterClient, REXSTER_URI, DEBUG

import time

# Default database. You can override this with the command line:
# $ python client_tests.py --db mydb
db_name = "tinkergraph"

#client = RexsterClient(db_name=db_name)
#client.config.set_logger(DEBUG)

class RexsterClientTestCase(ClientTestCase):

    def setUp(self):
        self.client = RexsterClient(db_name=db_name)

# Separated client index tests for Titan
class RexsterClientIndexTestCase(ClientIndexTestCase):

    def setUp(self):
        self.client = RexsterClient(db_name=db_name)
 
# automatic tests not currenly implemented... - JT
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
    suite.addTest(unittest.makeSuite(RexsterClientIndexTestCase))
    return suite

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default=None)
    args = parser.parse_args()
    
    db_name = args.db

    # Now set the sys.argv to the unittest_args (leaving sys.argv[0] alone)
    sys.argv[1:] = []
    
    unittest.main(defaultTest='rexster_client_suite')
