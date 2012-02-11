import unittest
from bulbs.config import Config
from bulbs.neo4jserver import Neo4jClient, NEO4J_URI
from bulbs.tests.client_tests import ClientTestCase

import time
import ujson as json

class Neo4jClientTestCase(ClientTestCase):

    def setUp(self):
        config = Config(NEO4J_URI)
        self.client = Neo4jClient(config)

class Neo4jIndexTestCase(unittest.TestCase):
    
    def setUp(self):
        config = Config(NEO4J_URI)
        self.client = Neo4jClient(config)

    #
    # Index Controller Tests
    #

    def test_create_vertex_index(self):
        index_name = "test_idxV"
        #keys = ["name","age"]
        self.client.delete_vertex_index(index_name)
        resp = self.client.create_vertex_index(index_name)
        #print resp.raw
        # cool...keys of "null" come back as None
        #new_keys = str(resp.results.get("keys"))
        #new_keys = json.loads(new_keys)
        #print type(new_keys), new_keys

    def test_get_vertex_index(self):
        index_name = "test_idxV"
        resp = self.client.get_vertex_index(index_name)
        #print "---------------------------"
        #print "RAW", resp.raw

    #
    # Index Container Tests
    #

    def test_indexed_vertex_CRUD(self):
        index_name = "test_idxV"
        data = dict(name="James Thornton",age=34)
        keys = ['name']
        #self.client.delete_vertex_index(index_name)
        resp = self.client.create_indexed_vertex(data,index_name,keys)
        #print "RAW", resp.raw        

        # update (update doesn't return data)
        _id = resp.results.get_id()
        #print "IDDDDDD", _id
        data = dict(name="James Thornton",age=35)
        keys = None
        resp = self.client.update_indexed_vertex(_id,data,index_name,keys)
        #print "RAW", resp.raw

        # delete
        resp = self.client.delete_vertex(_id)
        #print "RAW", resp.raw
        
    # deleting a vertex evidently removes it from its indices as well
    # maybe this is because you're using the Blueprints method
    #def test_delete_vertex(self):
    #    resp = self.client.delete_vertex(9)
    #    print "RAW", resp.raw


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

