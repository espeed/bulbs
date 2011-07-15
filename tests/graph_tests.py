import unittest
from bulbs import config
from bulbs.graph import Graph

class GraphTestCase(unittest.TestCase):

    def setUp(self):
        self.graph = Graph()

    def test_init(self):
        assert config.DATABASE_URL == self.graph.resource.db_url

    def test_V(self):
        vertices = self.graph.V
        vertices = list(vertices)
        assert len(vertices) > 0
        
    def test_E(self):
        edges = self.graph.E
        edges = list(edges)
        assert len(edges) > 0

    def test_idxV(self):
        self.graph.vertices.create({'name':'james'})
        vertices = self.graph.idxV(name="james")
        vertices = list(vertices)
        assert len(vertices) > 0
        
    def test_idxE(self):
        self.james = self.graph.vertices.create({'name':'James'})
        self.julie = self.graph.vertices.create({'name':'Julie'})
        self.graph.edges.create(self.james,"test",self.julie,{'time':'rightnow'})
        edges = self.graph.idxE(time="rightnow")
        edges = list(edges)
        assert len(edges) > 0

    #def test_clear(self):
    #    # WARNING: Be careful about uncommenting this. It will wipe your data.
    #    self.graph.clear()
    #    vertices = self.graph.V
    #    vertices = list(vertices)
    #    assert len(vertices) == 0
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(GraphTestCase))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

