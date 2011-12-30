import unittest
from bulbs.config import Config
from bulbs.neo4jserver import Neo4jResource, NEO4J_URI
from bulbs.tests.resource_tests import ResourceTestCase

import time
import ujson as json

class Neo4jResourceTestCase(ResourceTestCase):

    def setUp(self):
        config = Config(NEO4J_URI)
        self.resource = Neo4jResource(config)

class Neo4jIndexTestCase(unittest.TestCase):
    
    def setUp(self):
        config = Config(NEO4J_URI)
        config.debug = True
        self.resource = Neo4jResource(config)

    #
    # Index Controller Tests
    #

    def test_create_vertex_index(self):
        index_name = "test_idxV"
        keys = ["name","age"]
        self.resource.delete_vertex_index(index_name)
        resp = self.resource.create_vertex_index(index_name,keys=keys)
        #print resp.raw
        # cool...keys of "null" come back as None
        #new_keys = str(resp.results.get("keys"))
        #new_keys = json.loads(new_keys)
        #print type(new_keys), new_keys

    def test_get_vertex_index(self):
        index_name = "test_idxV"
        resp = self.resource.get_vertex_index(index_name)
        #print "---------------------------"
        #print "RAW", resp.raw

    #
    # Index Container Tests
    #

    def test_indexed_vertex_CRUD(self):
        index_name = "test_idxV"
        data = dict(name="James Thornton",age=34)
        keys = ['name']
        #self.resource.delete_vertex_index(index_name)
        resp = self.resource.create_indexed_vertex(data,index_name,keys)
        #print "RAW", resp.raw        

        # update (update doesn't return data)
        _id = resp.results.get_id()
        #print "IDDDDDD", _id
        data = dict(name="James Thornton",age=35)
        keys = None
        resp = self.resource.update_indexed_vertex(_id,data,index_name,keys)
        #print "RAW", resp.raw

        # delete
        resp = self.resource.delete_vertex(_id)
        #print "RAW", resp.raw
        
    # deleting a vertex evidently removes it from its indices as well
    # maybe this is because you're using the Blueprints method
    #def test_delete_vertex(self):
    #    resp = self.resource.delete_vertex(9)
    #    print "RAW", resp.raw


class TryTestCase(unittest.TestCase):
    
    def setUp(self):
        config = Config(NEO4J_URI)
        config.debug = True
        self.resource = Neo4jResource(config)

    #def test_warm_cache(self):
    #    resp = self.resource.warm_cache()
    #    print resp.raw

    def test_cypher(self):
        query = """START x  = node({_id}) MATCH x -[r]-> n RETURN type(r), n.name?, n.age?"""
        params = dict(_id=1261)
        resp = self.resource.cypher(query,params)
        #print resp.raw

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Neo4jResourceTestCase))
    suite.addTest(unittest.makeSuite(Neo4jIndexTestCase))
    #suite.addTest(unittest.makeSuite(TryTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

