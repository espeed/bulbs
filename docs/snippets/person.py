from bulbs.graph import Graph
from bulbs.element import  Vertex
from bulbs.datatype import Property, Integer, String
        
class Person(Vertex):

    element_type = "person"

    name = Property(String, nullable=False)
    age  = Property(Integer)

    def __init__(self,element=None,eid=None,**kwds):
        self.initialize(element,eid,kwds)

james = Person(name="James", age=34)
julie = Person(name="Julie", age=28)

Graph().edges.create(james,"knows",julie)


