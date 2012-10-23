import sys
import unittest
import argparse
from bulbs.config import Config, DEBUG
from bulbs.tests import BulbsTestCase, bulbs_test_suite
from bulbs.titan import Graph, TitanClient, TITAN_URI, \
    VertexIndexProxy, EdgeIndexProxy, KeyIndex
from bulbs.tests import GremlinTestCase

# Setting a module var looks to be the easiest way to do this
db_name = "tinkergraph"

def test_suite():
    # pass in a db_name to test a specific database
    client = TitanClient(db_name=db_name)
    BulbsTestCase.client = client
    BulbsTestCase.vertex_index_proxy = VertexIndexProxy
    BulbsTestCase.edge_index_proxy = EdgeIndexProxy
    BulbsTestCase.index_class = KeyIndex
    BulbsTestCase.graph = Graph(client.config)

    suite = bulbs_test_suite()
    #suite.addTest(unittest.makeSuite(RestTestCase))
    suite.addTest(unittest.makeSuite(GremlinTestCase))
    return suite

if __name__ == '__main__':

    # TODO: Bubble up the command line option to python setup.py test.
    # http://eli.thegreenplace.net/2011/08/02/python-unit-testing-parametrized-test-cases/
    # http://www.doughellmann.com/PyMOTW/argparse/

    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default="titanexample")
    args = parser.parse_args()
    
    db_name = args.db

    # Now set the sys.argv to the unittest_args (leaving sys.argv[0] alone)
    sys.argv[1:] = []

    unittest.main(defaultTest='test_suite')
