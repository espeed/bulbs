# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
import unittest

from bulbs.graph import Graph
from bulbs.element import Vertex
from bulbs import config

class VertexProxyTestCase(unittest.TestCase):

    def setUp(self):
        self.graph = Graph()
 
    def test_init(self):
        assert self.graph.resource.db_url == config.DATABASE_URL
        
    def test_create(self):
        james = self.graph.vertices.create({'name':'James'})
        assert isinstance(james,Vertex)
        int(james._id)
        assert james._type == "vertex"
        assert james.name == "James"

    def test_update(self):
        james = self.graph.vertices.create({'name':'James'})
        james = self.graph.vertices.update(james._id, {'name':'James','age':'34'})
        int(james._id)
        assert james._type == "vertex"
        assert james.name == "James"
        assert james.age == '34'

    def test_get(self):
        james = self.graph.vertices.create({'name':'James'})
        j2 = self.graph.vertices.get(james._id)
        assert james == j2

    def test_get_all(self):
        vertices = self.graph.vertices.get_all()
        vertices = list(vertices)
        assert len(vertices) > 0

    #def test_remove_property(self):
    #    query_time = self.graph.vertices.remove(self.james._id,'age')
    #    assert type(query_time) == float
    #    assert self.james.age is None

    def test_delete_vertex(self):
        james = self.graph.vertices.create({'name':'James'})
        resp = self.graph.vertices.delete(james)
        assert type(resp.query_time) == float
        j2 = self.graph.vertices.get(james._id)
        assert j2 == None


class VertexTestCase(unittest.TestCase):
    
    def setUp(self):
        self.graph = Graph()
        self.james = self.graph.vertices.create({'name':'James'})
        self.julie = self.graph.vertices.create({'name':'Julie'})
        assert isinstance(self.james,Vertex)
        self.graph.edges.create(self.james,"test",self.julie)
        self.graph.edges.create(self.julie,"test",self.james)
        
    def test_init(self):
        int(self.james._id)
        assert self.james._type == "vertex"
        assert self.james.name == "James"

    def test_get_out_edges(self):
        edges = self.james.outE()
        edges = list(edges)
        assert len(edges) == 1

    def test_get_in_edges(self):
        edges = self.james.inE()
        edges = list(edges)
        assert len(edges) == 1

    def test_get_both_edges(self):
        edges = self.james.bothE()
        edges = list(edges)
        assert len(edges) == 2

    def test_get_both_labeled_edges(self):
        edges = self.james.bothE("test")
        edges = list(edges)
        assert len(edges) == 2

class EdgeProxyTestCase(unittest.TestCase):

    def setUp(self):
        self.graph = Graph()
        self.james = self.graph.vertices.create({'name':'James'})
        self.julie = self.graph.vertices.create({'name':'Julie'})
        
    def test_create(self):
        edge = self.graph.edges.create(self.james,"test",self.julie)
        assert edge._outV == self.james._id
        assert edge._label == "test"
        assert edge._inV == self.julie._id
        
    def test_update(self):
        e1 = self.graph.edges.create(self.james,"test",self.julie,{'time':'today'})
        assert e1.time == 'today'
        e2 = self.graph.edges.update(e1._id,{'time':'tomorrow'})
        assert e1._id == e2._id
        assert e1._inV == e2._inV
        assert e1._label == e2._label
        assert e1._outV == e2._outV
        assert e2.time == 'tomorrow'

    def test_get(self):
        e1 = self.graph.edges.create(self.james,"test",self.julie,{'time':'today'})
        e2 = self.graph.edges.get(e1._id)
        assert e1 == e2

    def test_get_all(self):
        edges = self.graph.edges.get_all()
        edges = list(edges)
        assert type(edges) == list

    #def test_remove_property(self):
    #    e1 = self.graph.edges.create(self.james,"test",self.julie,{'time':'today'})
    #    query_time = self.graph.edges.remove(e1._id,{'time'})
    #    assert type(query_time) == float
    #    assert e1.time is None

    def test_delete_edge(self):
        e1 = self.graph.edges.create(self.james,"test",self.julie)
        resp = self.graph.edges.delete(e1)
        assert type(resp.query_time) == float
        e2 = self.graph.edges.get(e1._id)
        assert e2 == None
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(VertexProxyTestCase))
    suite.addTest(unittest.makeSuite(VertexTestCase))
    suite.addTest(unittest.makeSuite(EdgeProxyTestCase))
    # NOTE: there are no tests for the Edge because it doesn't have methods.

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

