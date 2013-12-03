import unittest

from .rest_tests import RestTestCase
from .element_tests import VertexTestCase, VertexProxyTestCase, EdgeProxyTestCase
from .graph_tests import GraphTestCase
from .index_tests import IndexTestCase
from .model_tests import NodeTestCase, RelationshipTestCase
from .gremlin_tests import GremlinTestCase
from .testcase import BulbsTestCase



def bulbs_test_suite():

    suite = unittest.TestSuite()
    #suite.addTest(unittest.makeSuite(RestTestCase))
    suite.addTest(unittest.makeSuite(VertexTestCase))
    suite.addTest(unittest.makeSuite(VertexProxyTestCase))
    suite.addTest(unittest.makeSuite(EdgeProxyTestCase))
    # TODO: Add automatic/key-index tests
    #try:
        # Temporary hack...
        # The IndexTestCase currently only tests manual indices
        # but Titan only uses an automatic KeyIndex, and 
        # its index_type is hardcoded to "automatic"
        # index_type is a property that requires results being set so
        # it will barf if it's not hardcoded like Titan
        # so if it barfs, we know it's a manual index and thus
        # we want to run the test
     #   BulbsTestCase.index_class(None, None).index_type
      #  print "NOT RUNNING INDEX TESTS..."
        # don't run the test for Titan
    #except:
    suite.addTest(unittest.makeSuite(IndexTestCase))
    suite.addTest(unittest.makeSuite(NodeTestCase))
    suite.addTest(unittest.makeSuite(RelationshipTestCase))
    suite.addTest(unittest.makeSuite(GraphTestCase))
    #suite.addTest(unittest.makeSuite(GremlinTestCase))


    return suite
