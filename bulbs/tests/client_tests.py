import unittest
import random

from bulbs.config import Config
from bulbs.registry import Registry
from bulbs.base import TypeSystem

class ClientTestCase(unittest.TestCase):
    
    def setUp(self):
        self.client = None
        raise NotImplementedError

    # Some server implementations (Rexster) return a 404 if index doesn't exist
    def _delete_vertex_index(self,index_name):
        try:
            self.client.delete_vertex_index(index_name)
        except LookupError:
            pass

    def _delete_edge_index(self,index_name):
        try:
            self.client.delete_edge_index(index_name)
        except LookupError:
            pass


    def test_init(self):
        
        assert self.client.default_uri is not None
        assert isinstance(self.client.config, Config) 
        assert isinstance(self.client.registry, Registry)
        assert isinstance(self.client.type_system, TypeSystem)

    # Vertex Proxy

    def test_create_vertex(self):
        name, age = "James", 34
        data = dict(name=name, age=age)
        resp = self.client.create_vertex(data)
        assert resp.results.get_type() == "vertex"
        assert resp.results.get_data() == data  
        assert resp.results.data.get('name') == name
        assert resp.results.data.get('age') == age
  
    def test_get_vertex(self):
        name, age = "James", 34
        data = dict(name=name,age=age)
        resp1 = self.client.create_vertex(data)
        resp2 = self.client.get_vertex(resp1.results.get_id())
        assert resp1.results.data == resp2.results.data

    def test_get_all_vertices(self):
        resp = self.client.get_all_vertices()
        assert resp.total_size > 1

    def test_update_vertex(self):
        name1, age1 = "James", 34
        data1 = dict(name=name1, age=age1)
        resp1 = self.client.create_vertex(data1)        

        name2, age2 = "Julie", 28
        data2 = dict(name=name2,age=age2)
        resp2 = self.client.update_vertex(resp1.results.get_id(), data2)

        resp3 = self.client.get_vertex(resp1.results.get_id())

        assert resp3.results.get_type() == "vertex"
        assert resp3.results.data.get('name') == name2
        assert resp3.results.data.get('age') == age2

    def test_delete_vertex(self):
        name, age = "James", 34
        data = dict(name=name,age=age)
        resp1 = self.client.create_vertex(data)        

        deleted = False
        resp2 = self.client.delete_vertex(resp1.results.get_id())
        try:
            resp3 = self.client.get_vertex(resp1.results.get_id())
        except LookupError:
            deleted = True
        assert deleted is True

    # Edges
    def test_create_edge(self):
        resp1 = self.client.create_vertex({'name':'James','age':34})
        resp2 = self.client.create_vertex({'name':'Julie','age':28})

        outV = resp1.results.get_id()
        inV = resp2.results.get_id()
        label = "knows"
        data = dict(timestamp=123456789)
        resp3 = self.client.create_edge(outV, label, inV, data)

        assert resp3.results.get_type() == "edge"
        assert resp3.results.get_label() == label
        assert resp3.results.get_outV() == outV
        assert resp3.results.get_inV() == inV
        assert resp3.results.get_data() == data

    def test_get_edge(self):
        resp1 = self.client.create_vertex({'name':'James','age':34})
        resp2 = self.client.create_vertex({'name':'Julie','age':28})

        outV = resp1.results.get_id()
        inV = resp2.results.get_id()
        label = "knows"

        resp3 = self.client.create_edge(outV,label,inV)
        resp4 = self.client.get_edge(resp3.results.get_id())

        assert resp3.results.get_id() == resp4.results.get_id()
        assert resp3.results.get_type() == resp4.results.get_type()
        assert resp3.results.get_data() == resp4.results.get_data()

    def test_get_all_edges(self):
        resp1 = self.client.create_vertex({'name':'James','age':34})
        resp2 = self.client.create_vertex({'name':'Julie','age':28})

        outV = resp1.results.get_id()
        inV = resp2.results.get_id()
        label = "knows"
        data = dict(timestamp=123456789)
        resp3 = self.client.create_edge(outV, label, inV, data)
        resp4 = self.client.create_edge(inV, label, outV, data)

        resp = self.client.get_all_edges()
        assert resp.total_size > 1

    def test_update_edge(self):
        resp1 = self.client.create_vertex({'name':'James','age':34})
        resp2 = self.client.create_vertex({'name':'Julie','age':28})

        outV = resp1.results.get_id()
        inV = resp2.results.get_id()
        label = "knows"
        resp3 = self.client.create_edge(outV,label,inV)

        data = dict(timestamp=12345678)
        resp4 = self.client.update_edge(resp3.results.get_id(),data)

        assert resp4.results.get_data() == data

    def test_delete_edge(self):
        resp1 = self.client.create_vertex({'name':'James','age':34})
        resp2 = self.client.create_vertex({'name':'Julie','age':28})
        outV = resp1.results.get_id()
        inV = resp2.results.get_id()
        label = "knows"
        resp3 = self.client.create_edge(outV,label,inV)

        deleted = False
        resp4 = self.client.delete_edge(resp3.results.get_id())
        try:
            resp4 = self.client.get_edge(resp3.results.get_id())
        except LookupError:
            deleted = True
        assert deleted is True


    def test_vertex_container(self):
        resp1 = self.client.create_vertex({'name':'James','age':34})
        resp2 = self.client.create_vertex({'name':'Julie','age':28})

        outV = vertex_id1 =resp1.results.get_id()
        inV = vertex_id2 = resp2.results.get_id()
        label = "knows"

        resp3 = self.client.create_edge(outV, label, inV)
        edge_id = resp3.results.get_id()

        # Get the outgoing edge of vertex1
        outE = self.client.outE(vertex_id1).one()
        assert outE.get_id() == edge_id

        # Get the incoming edge of vertex2
        inE = self.client.inE(vertex_id2).one()
        assert inE.get_id() == edge_id

        # Get the incoming and outgoing edges of vertex1
        bothE = self.client.outE(vertex_id1).one()
        assert bothE.get_id() == edge_id
        
        # Get the outgoing edge of vertex1
        outV = self.client.outV(vertex_id1).one()
        assert outV.get_id() == vertex_id2

        # Get the incoming edge of vertex2
        inV = self.client.inV(vertex_id2).one()
        assert inV.get_id() == vertex_id1

        # Get the incoming and outgoing edges of vertex1
        bothV = self.client.outV(vertex_id1).one()
        assert bothV.get_id() == vertex_id2


    # Index Controller Tests

    def test_create_vertex_index(self):
        index_name = "test_idxV"
        self._delete_vertex_index(index_name)
        resp = self.client.create_vertex_index(index_name)

        assert resp.results.get_index_class() == "vertex"        
        assert resp.results.get_index_name() == index_name
                
    def test_get_vertex_index(self):
        index_name = "test_idxV"
        resp = self.client.get_vertex_index(index_name)

        assert resp.results.get_index_class() == "vertex"        
        assert resp.results.get_index_name() == index_name


    # Index Container Tests

    def test_indexed_vertex_CRUD(self):
        index_name = "test_idxV"
        self._delete_vertex_index(index_name)
        self.client.create_vertex_index(index_name)

        # Create and Index Vertex
        name1 = "James %s" % random.random()
        age1 = 34
        data1 = dict(name=name1, age=age1)
        keys1 = ['name']
        self.client.create_indexed_vertex(data1, index_name, keys1)
        
        # Lookup Vertex
        resp1 = self.client.lookup_vertex(index_name, "name", name1)
        results1 = resp1.results.next()

        assert results1.get_type() == "vertex"
        assert results1.get_data() == data1  
        assert results1.data.get('name') == name1
        assert results1.data.get('age') == age1

        # Update and Index Vertex (update doesn't return data)
        _id = results1.get_id()
        name2 = "James Thornton %s" % random.random()
        age2 = 35
        data2 = dict(name=name2, age=age2)
        keys2 = None
        self.client.update_indexed_vertex(_id, data2, index_name, keys2)

        # Lookup Vertex
        resp2 = self.client.lookup_vertex(index_name, "name", name2)
        result2 = resp2.results.next()

        assert result2.get_type() == "vertex"
        assert result2.get_data() == data2
        assert result2.data.get('name') == name2
        assert result2.data.get('age') == age2

        # Remove a vertex from the index
        self.client.remove_vertex(index_name, _id, "name", name2)
        
        resp3 = self.client.lookup_vertex(index_name, "name", name2)
        assert resp3.total_size == 0
        

    def test_indexed_edge_CRUD(self):
        index_name = "test_idxE"
        self._delete_edge_index(index_name)
        self.client.create_edge_index(index_name)

        respV1 = self.client.create_vertex({'name':'James','age':34})
        respV2 = self.client.create_vertex({'name':'Julie','age':28})
        V1_id = respV1.results.get_id()
        V2_id = respV2.results.get_id()

        # Create and Index Edge
        city1 = "Dallas"
        data1 = dict(city=city1)
        keys1 = ['city']
        resp = self.client.create_indexed_edge(V1_id, "knows", V2_id, data1, index_name, keys1)
        
        # Lookup Edge
        resp1 = self.client.lookup_edge(index_name, "city", city1)
        results1 = resp1.results.next()

        assert results1.get_type() == "edge"
        assert results1.get_data() == data1  
        assert results1.data.get('city') == city1

        # Update and Index Edge (update doesn't return data)
        _id = results1.get_id()
        city2 = "Austin"
        data2 = dict(city=city2)
        keys2 = ['city']
        self.client.update_indexed_edge(_id, data2, index_name, keys2)

        # Lookup Edge
        resp2 = self.client.lookup_edge(index_name, "city", city2)
        result2 = resp2.results.next()

        assert result2.get_type() == "edge"
        assert result2.get_data() == data2
        assert result2.data.get('city') == city2

        # Remove and edge from the index
        self.client.remove_edge(index_name, _id, "city", city2)
        
        resp3 = self.client.lookup_edge(index_name, "city", city2)
        assert resp3.total_size == 0
        


