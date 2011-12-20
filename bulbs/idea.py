from bulbs.config import Config, REXSTER_URI
from bulbs.rexster import RexsterResource
from bulbs.graph import Graph, RexsterGraph, RexsterIndex
from bulbs.model import Node, NodeProxy
from bulbs.property import Property, String, Integer
from bulbs.element import Vertex, VertexProxy, EdgeProxy, Edge
from bulbs.index import IndexProxy
from bulbs.gremlin import Gremlin

from collections import OrderedDict

class Idea(Node):

    element_type = "idea"
    
    text = Property(String,nullable=False)
    age = Property(Integer)

    default_index = "ideas"

print "ET", Idea.element_type
    
class Whybase(Graph):

    def __init__(self):
        self.config = Config("http://localhost:8182/graphs/test")
        self.config.debug = True
        self.resource = RexsterResource(self.config)

        self.gremlin = Gremlin(self.resource)        
        self.indices = IndexProxy(RexsterIndex,self.resource)
        
        #self.vertices = VertexProxy(Vertex,self.resource)
        #self.vertices.index = self.indices.get("vertices")
 
        #self.edges = EdgeProxy(Edge,self.resource)
        #self.edges.index = self.indices.get("edges")

        self.ideas = NodeProxy(Idea,self.resource)
        self.ideas.index = self.indices.get_or_create("ideas",Idea,[name,age])


whybase = Whybase()
#idea = whybase.ideas.create(text="hello world",age="34")
#print type(idea), idea.eid, idea.text, idea.age, idea.element_type

#print whybase.resource.create_indexed_vertex().raw

idea = whybase.ideas.create(text="James",age=34)

print type(idea), idea.text, idea.age, idea._result.data

idea.text = "hello world"
idea.age = 21
idea.save()

#print type(idea), idea.text, idea.age, idea._result.data

#print list(whybase.ideas.get_all())
