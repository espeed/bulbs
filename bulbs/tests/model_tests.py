import unittest
from testcase import BulbsTestCase
from bulbs.index import IndexProxy
from bulbs.model import Node, NodeProxy, Relationship, RelationshipProxy
from bulbs.property import Property, Integer, String, Float

class Knows(Relationship):

    label = "knows"
    timestamp = Property(Float)

class Person(Node):

    element_type = "person"
    
    name = Property(String, nullable=False)
    age  = Property(Integer)



class NodeTestCase(BulbsTestCase):

    def setUp(self):
        indices = self.vertex_index_proxy(self.index_class,self.resource)
        self.people = NodeProxy(Person,self.resource)
        self.people.index = indices.get_or_create("people")
        self.james = self.people.create(name="James", age=34)

    def test_properties(self):
        assert type(self.james.eid) == int
        assert self.james.element_type == "person"
        assert self.james.name == "James"
        assert self.james.age == 34

    def test_get(self):
        person = self.people.get(self.james.eid)
        assert person == self.james
        
    def test_get_all(self):
        people = self.people.get_all()
        assert len(list(people)) > 1
        
    def test_index_name(self):
        index_name = self.people.index.index_name
        assert index_name == "people"

    # Will this work for autmatic indices?
    #def test_index_put_and_get(self): 
        # must test put/get together b/c self.james gets reset every time
     #   self.people.index.put(self.james.eid,age=self.james.age)
     #   james = self.people.index.get_unique("age",'34')
     #   assert self.james == james
        #Person.remove(self.james.eid,dict(age="34"))


class RelationshipTestCase(BulbsTestCase):

    def setUp(self):
        indices = self.vertex_index_proxy(self.index_class,self.resource)
        self.people = NodeProxy(Person,self.resource)
        self.knows = RelationshipProxy(Knows,self.resource)
        self.people.index = indices.get_or_create("people")
        self.james = self.people.create(name="James", age=34)
        self.julie = self.people.create(name="Julie", age=28)
        #self.relationship = Relationship.create(self.james,"knows",self.julie)
        
    def test_properties(self):
        self.relationship = self.knows.create(self.james,self.julie)
        assert self.relationship._label == "knows"
        assert self.relationship.outV()._id == self.james.eid
        assert self.relationship.inV()._id == self.julie.eid

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NodeTestCase))
    suite.addTest(unittest.makeSuite(RelationshipTestCase))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

