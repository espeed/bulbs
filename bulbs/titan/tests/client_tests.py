import sys
import argparse

import unittest
from bulbs.config import Config
from bulbs.tests.client_tests import ClientTestCase
from bulbs.tests.client_index_tests import ClientIndexTestCase
from bulbs.titan.client import TitanClient, TITAN_URI, DEBUG

import time

# Default database. You can override this with the command line:
# $ python client_tests.py --db mydb
db_name = "graph"

#client = TitanClient(db_name=db_name)
#client.config.set_logger(DEBUG)

class TitanClientTestCase(ClientTestCase):

    def setUp(self):
        self.client = TitanClient(db_name=db_name)

# Separated client index tests for Titan
class TitanClientIndexTestCase(ClientIndexTestCase):

    def setUp(self):
        self.client = TitanClient(db_name=db_name)
        
    def test_create_vertex_index(self):
        pass

    def test_get_vertex_index(self):
        pass

    def test_indexed_vertex_CRUD(self):
        pass

    def test_indexed_edge_CRUD(self):
        pass


def titan_client_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TitanClientTestCase))
    suite.addTest(unittest.makeSuite(TitanClientIndexTestCase))
    return suite

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default=None)
    args = parser.parse_args()
    
    db_name = args.db

    # Now set the sys.argv to the unittest_args (leaving sys.argv[0] alone)
    sys.argv[1:] = []
    
    unittest.main(defaultTest='titan_client_suite')
