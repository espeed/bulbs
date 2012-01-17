import unittest

class ResourceTestCase(unittest.TestCase):
    
    def setUp(self):
        #    self.resource = RexsterResource()
        #    self.vertex_type = "vertex"
        #    self.edge_type = "edge"
        #raise NotImplemented
        pass

    # Vertices
    def test_create_vertex(self):
        name, age = "James", 34
        data = dict(name=name,age=age)
        resp = self.resource.create_vertex(data)
        #print resp.raw
        assert type(resp.results.get_id()) == int
        assert resp.results.get_type() == "vertex"
        assert resp.results.data.get('name') == name
        assert resp.results.data.get('age') == age
        
    def test_get_vertex(self):
        name, age = "James", 34
        data = dict(name=name,age=age)
        resp1 = self.resource.create_vertex(data)
        resp2 = self.resource.get_vertex(resp1.results.get_id())
        assert resp1.results.data == resp2.results.data

    def test_update_vertex(self):
        name, age = "James", 34
        data = dict(name=name,age=age)
        resp1 = self.resource.create_vertex(data)        
        name, age = "Julie", 28
        data = dict(name=name,age=age)
        resp2 = self.resource.update_vertex(resp1.results.get_id(),data)
        resp3 = self.resource.get_vertex(resp1.results.get_id())
        assert type(resp3.results.get_id()) == int
        assert resp3.results.get_type() == "vertex"
        assert resp3.results.data.get('name') == name
        assert resp3.results.data.get('age') == age

    def test_delete_vertex(self):
        name, age = "James", 34
        data = dict(name=name,age=age)
        resp1 = self.resource.create_vertex(data)        
        resp2 = self.resource.delete_vertex(resp1.results.get_id())
        try:
            resp3 = self.resource.get_vertex(resp1.results.get_id())
        except LookupError:
            pass

    # Edges
    def test_create_edge(self):
        resp1 = self.resource.create_vertex({'name':'James','age':34})
        resp2 = self.resource.create_vertex({'name':'Julie','age':28})
        outV = resp1.results.get_id()
        inV = resp2.results.get_id()
        label = "knows"
        resp3 = self.resource.create_edge(outV,label,inV)
        assert type(resp3.results.get_id()) == int
        assert resp3.results.get_type() == "edge"
        assert resp3.results.get_label() == label
        assert resp3.results.get_outV() == outV
        assert resp3.results.get_inV() == inV

    def test_get_edge(self):
        resp1 = self.resource.create_vertex({'name':'James','age':34})
        resp2 = self.resource.create_vertex({'name':'Julie','age':28})
        outV = resp1.results.get_id()
        inV = resp2.results.get_id()
        label = "knows"
        resp3 = self.resource.create_edge(outV,label,inV)
        resp4 = self.resource.get_edge(resp3.results.get_id())
        assert resp3.results.data == resp4.results.data

    def test_delete_edge(self):
        resp1 = self.resource.create_vertex({'name':'James','age':34})
        resp2 = self.resource.create_vertex({'name':'Julie','age':28})
        outV = resp1.results.get_id()
        inV = resp2.results.get_id()
        label = "knows"
        resp3 = self.resource.create_edge(outV,label,inV)
        try:
            resp4 = self.resource.delete_edge(resp3.results.get_id())
            pass
        except LookupError:
            pass

    def test_update_edge(self):
        resp1 = self.resource.create_vertex({'name':'James','age':34})
        resp2 = self.resource.create_vertex({'name':'Julie','age':28})
        outV = resp1.results.get_id()
        inV = resp2.results.get_id()
        label = "knows"
        resp3 = self.resource.create_edge(outV,label,inV)
        data = dict(timestamp=12345678)
        resp4 = self.resource.update_edge(resp3.results.get_id(),data)
       

    def test_gremlin(self):
        # limiting return count so we don't exceed heap size
        resp = self.resource.gremlin("g.V[0..9]")
        assert resp.total_size > 5



