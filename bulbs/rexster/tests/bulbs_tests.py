import unittest
from bulbs.config import Config, DEBUG
from bulbs.tests import BulbsTestCase, bulbs_test_suite
from bulbs.rexster import RexsterResource, REXSTER_URI, \
    VertexIndexProxy, EdgeIndexProxy, ManualIndex


config = Config(REXSTER_URI)
BulbsTestCase.resource = RexsterResource(config)
BulbsTestCase.vertex_index_proxy = VertexIndexProxy
BulbsTestCase.edge_index_proxy = EdgeIndexProxy
BulbsTestCase.index_class = ManualIndex

if __name__ == '__main__':
    suite = bulbs_test_suite()
    #suite.addTest(unittest.makeSuite(RestTestCase))
    #suite.addTest(unittest.makeSuite(GremlinTestCase))
    unittest.main(defaultTest='suite')
