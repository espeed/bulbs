from uuid import uuid1
import unittest
from bulbs.config import Config
from bulbs.utils import json
from bulbs.neo4jserver import Neo4jClient, NEO4J_URI
from bulbs.tests.client_tests import ClientTestCase
from bulbs.tests.client_index_tests import ClientIndexTestCase

from bulbs.factory import Factory
from bulbs.element import Vertex, Edge
from bulbs.neo4jserver.index import ExactIndex

import time


class Neo4jClientTestCase(ClientTestCase):

    def setUp(self):
        config = Config(NEO4J_URI)
        self.client = Neo4jClient(config)


# Separated client index tests for Titan
class Neo4jClientIndexTestCase(ClientIndexTestCase):

    def setUp(self):
        config = Config(NEO4J_URI)
        self.client = Neo4jClient(config)

    def test_create_unique_vertex(self):
        idx_name = 'test_idx'
        self._delete_vertex_index(idx_name)
        self.client.create_vertex_index(idx_name)

        k, v = 'key', uuid1().get_hex()
        args = (k, v, {k: v})
        resp = self.client.create_unique_vertex(idx_name, *args)
        assert resp.headers['status'] == '201'
        assert resp.results.data.get(k) == v

        resp = self.client.create_unique_vertex(idx_name, *args)
        assert resp.headers['status'] == '200'
        assert resp.results.data.get(k) == v


# why is this here? - JT 10/22/2012
class Neo4jIndexTestCase(unittest.TestCase):
    
    def setUp(self):
        config = Config(NEO4J_URI)
        self.client = Neo4jClient(config)
        self.factory = Factory(self.client)

    def test_gremlin(self):
        # limiting return count so we don't exceed heap size
        resp = self.client.gremlin("g.V[0..9]")
        assert resp.total_size > 5

    def test_query_exact_vertex_index(self):
        index = self.factory.get_index(Vertex, ExactIndex)
        vertices = index.query("name", "Jam*")
        assert len(list(vertices)) > 1

    def test_query_exact_edge_index(self):
        index = self.factory.get_index(Edge, ExactIndex)
        edges = index.query("timestamp", "1*")
        assert len(list(edges)) > 1

    def test_create_unique_vertex(self):
        index = self.factory.get_index(Vertex, ExactIndex)
        k, v = 'key', uuid1().get_hex()
        args = (k, v, {k: v})

        vertex, created = index.create_unique_vertex(*args)
        assert isinstance(vertex, Vertex)
        assert created is True

        vertex, created = index.create_unique_vertex(*args)
        assert isinstance(vertex, Vertex)
        assert created is False


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
    suite.addTest(unittest.makeSuite(Neo4jClientIndexTestCase))
    suite.addTest(unittest.makeSuite(Neo4jIndexTestCase))
    #suite.addTest(unittest.makeSuite(GremlinTestCase))
    #suite.addTest(unittest.makeSuite(CypherTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='neo4j_client_suite')

