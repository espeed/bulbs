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
    if BulbsTestCase.index_class(None, None).index_type is "manual":
        suite.addTest(unittest.makeSuite(IndexTestCase))
    suite.addTest(unittest.makeSuite(NodeTestCase))
    suite.addTest(unittest.makeSuite(RelationshipTestCase))
    suite.addTest(unittest.makeSuite(GraphTestCase))
    #suite.addTest(unittest.makeSuite(GremlinTestCase))


    return suite
