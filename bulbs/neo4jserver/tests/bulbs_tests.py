import unittest
from bulbs.tests import BulbsTestCase, suite
from bulbs.config import Config
from bulbs.neo4jserver import Neo4jResource, Neo4jIndex, NEO4J_URI

config = Config(NEO4J_URI)
BulbsTestCase.resource = Neo4jResource(config)
BulbsTestCase.index_class = Neo4jIndex

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
