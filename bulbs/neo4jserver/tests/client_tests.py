import unittest
from bulbs.config import Config
from bulbs.utils import json
from bulbs.neo4jserver import Neo4jClient, NEO4J_URI
from bulbs.tests.client_tests import ClientTestCase

import time


class Neo4jClientTestCase(ClientTestCase):

    def setUp(self):
        config = Config(NEO4J_URI)
        self.client = Neo4jClient(config)

class Neo4jIndexTestCase(unittest.TestCase):
    
    def setUp(self):
        config = Config(NEO4J_URI)
        self.client = Neo4jClient(config)

    def test_gremlin(self):
        # limiting return count so we don't exceed heap size
        resp = self.client.gremlin("g.V[0..9]")
        assert resp.total_size > 5



class CypherTestCase(unittest.TestCase):
    
    def setUp(self):
        config = Config(NEO4J_URI)
        self.client = Neo4jClient(config)

    #def test_warm_cache(self):
    #    resp = self.client.warm_cache()
    #    print resp.raw

    def test_cypher(self):
        query = """START x  = node({_id}) MATCH x -[r]-> n RETURN type(r), n.name?, n.age?"""
        params = dict(_id=1261)
        resp = self.client.cypher(query,params)
        #print resp.raw

def neo4j_client_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Neo4jClientTestCase))
    suite.addTest(unittest.makeSuite(Neo4jIndexTestCase))
    #suite.addTest(unittest.makeSuite(GremlinTestCase))
    #suite.addTest(unittest.makeSuite(CypherTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='neo4j_client_suite')

