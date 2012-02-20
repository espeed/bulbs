import unittest
from bulbs.config import Config
#from bulbs.rest import Request

from bulbs.utils import build_path
from bulbs.rexster.client import RexsterRequest

class RestTestCase(unittest.TestCase):
    
    def setUp(self):
        #self.client = Client(config.DATABASE_URL)
        config = Config(root_uri=None)
        self.request = RexsterRequest(config)

    def test_init(self):
        config = Config('http://localhost:8182/not-graphs/gratefulgraph')
        assert config.root_uri == 'http://localhost:8182/not-graphs/gratefulgraph'

    def test_post(self):
        name_in = "james"
        email_in = "james@jamesthornton.com"

        path = build_path("vertices")
        params = dict(name=name_in, email=email_in)
        resp = self.request.post(path,params)
                
        assert resp.results._type == 'vertex'
        assert name_in == resp.results.get('name') 
        assert email_in == resp.results.get('email')

        # use the results of this function for get and delete tests 
        return resp
        
    def test_get(self):
        resp1 = self.test_post()
        oid1 = resp1.results.get('_id')
        element_type1 = resp1.results.get('_type')
        name1 = resp1.results.get('name')
        email1 = resp1.results.get('email')

        path = build_path("vertices",oid1)
        params = dict(name=name1, email=email1)
        resp2 = self.request.get(path,params)

        assert oid1 == resp2.results.get('_id')
        assert element_type1 == resp2.results.get('_type')
        assert name1 == resp2.results.get('name')
        assert email1 == resp2.results.get('email')

    def test_delete(self):

        resp1 = self.test_post()
        oid1 = resp1.results.get('_id')
        name1 = resp1.results.get('name')
        email1 = resp1.results.get('email')

        # make sure it's there
        #assert type(oid1) == int

        # delete it
        path = build_path("vertices",oid1)
        params = dict(name=name1, email=email1)
        resp2 = self.request.delete(path,params)

        # verify it's gone
        #assert "SNAPSHOT" in resp2.rexster_version
        #assert type(resp2.get('query_time')) == float
        assert resp2.results == None


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RestTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

