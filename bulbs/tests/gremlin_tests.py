import unittest
from testcase import BulbsTestCase

class GremlinTestCase(BulbsTestCase):

    def setUp(self):
        #    self.resource = RexsterResource()
        #    self.vertex_type = "vertex"
        #    self.edge_type = "edge"
        #raise NotImplemented
        pass

    def test_gremlin(self):
        # limiting return count so we don't exceed heap size
        resp = self.resource.gremlin("g.V[0..9]")
        assert resp.total_size > 5
