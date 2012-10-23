import unittest
import random

from bulbs.config import Config, DEBUG, ERROR
from bulbs.registry import Registry
from bulbs.base import TypeSystem

class ClientIndexTestCase(unittest.TestCase):
    
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
        results1 = next(resp1.results)

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
        result2 = next(resp2.results)

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
        results1 = next(resp1.results)

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
        result2 = next(resp2.results)

        assert result2.get_type() == "edge"
        assert result2.get_data() == data2
        assert result2.data.get('city') == city2

        # Remove and edge from the index
        self.client.remove_edge(index_name, _id, "city", city2)
        
        resp3 = self.client.lookup_edge(index_name, "city", city2)
        assert resp3.total_size == 0
        


