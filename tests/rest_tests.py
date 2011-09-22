import unittest
from bulbs import config
from bulbs.rest import Resource


class RestTestCase(unittest.TestCase):
    
    def setUp(self):
        self.resource = Resource(config.DATABASE_URL)

    def test_init(self):
        res = Resource('http://localhost:8182/not-graphs/gratefulgraph')

        assert res.base_url == 'http://localhost:8182/not-graphs'
        assert res.db_name == 'gratefulgraph'

    def test_post(self):
        name_in = "james"
        email_in = "james@jamesthornton.com"

        target = "%s/%s" % (self.resource.db_name, "vertices")
        params = dict(name=name_in, email=email_in)
        resp = self.resource.post(target,params)
                
        oid = int(resp.results['_id'])
        element_type = resp.results['_type']
        name_out = resp.results['name']
        email_out = resp.results['email']
        
        assert type(resp.results) == dict
        assert type(oid) == int
        assert element_type == 'vertex'
        assert name_in == name_out 
        assert email_in == email_out

        # use the results of this function for get and delete tests 
        return resp
        
    def test_get(self):
        resp1 = self.test_post()
        oid1 = int(resp1.results['_id'])
        element_type1 = resp1.results['_type']
        name1 = resp1.results['name']
        email1 = resp1.results['email']

        target = "%s/%s/%d" % (self.resource.db_name, "vertices", oid1)
        params = dict(name=name1, email=email1)
        
        resp2 = self.resource.get(target,params)
        oid2 = int(resp2.results['_id'])
        element_type2 = resp2.results['_type']
        name2 = resp2.results['name']
        email2 = resp2.results['email']

        assert oid1 == oid2
        assert element_type1 == element_type2
        assert name1 == name2
        assert email1 == email2

    def test_delete(self):

        resp1 = self.test_post()
        oid1 = int(resp1.results['_id'])
        name1 = resp1.results['name']
        email1 = resp1.results['email']

        # make sure it's there
        assert type(oid1) == int

        # delete it
        target = "%s/%s/%d" % (self.resource.db_name, "vertices", oid1)
        params = dict(name=name1, email=email1)

        resp2 = self.resource.delete(target,params)

        # verify it's gone
        assert "SNAPSHOT" in resp2.rexster_version
        assert type(resp2.query_time) == float
        assert resp2.results == None


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RestTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

