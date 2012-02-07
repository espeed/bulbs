import unittest
from bulbs.config import Config
from bulbs.tests import BulbsTestCase, bulbs_test_suite
from bulbs.tests import GremlinTestCase
from bulbs.neo4jserver import Neo4jResource, NEO4J_URI, \
   VertexIndexProxy, EdgeIndexProxy, ExactIndex


config = Config(NEO4J_URI)
BulbsTestCase.resource = Neo4jResource(config)
BulbsTestCase.vertex_index_proxy = VertexIndexProxy
BulbsTestCase.edge_index_proxy = EdgeIndexProxy
BulbsTestCase.index_class = ExactIndex

def test_suite():
    suite = bulbs_test_suite()
    #suite.addTest(unittest.makeSuite(RestTestCase))
    suite.addTest(unittest.makeSuite(GremlinTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

