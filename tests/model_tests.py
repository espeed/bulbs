import unittest
from bulbs.model import Node, Relationship
from bulbs.property import Property, Integer, String

class Person(Node):

    element_type = "person"
    
    name = Property(String, nullable=False)
    age  = Property(Integer)

class NodeTestCase(unittest.TestCase):

    def setUp(self):
        self.james = Person(name="James", age=34)

    def test_properties(self):
        int(self.james.eid)
        assert self.james.element_type == "person"
        assert self.james.name == "James"
        assert self.james.age == 34

    def test_get(self):
        person = Person.get(self.james.eid)
        assert person == self.james
        
    def test_get_all(self):
        people = Person.get_all()
        assert len(list(people)) > 1
        
    def test_get_element_key(self):
        element_key = Person._get_element_key()
        assert element_key == "person"

    def test_index_name(self):
        index_name = Person._get_index_name()
        assert index_name == "person"

    def test_create_index(self):
        Person.delete_index()
        Person.create_index()
       
    def test_index_put_and_get(self): 
        # must test put/get together b/c self.james gets reset every time
        Person.index.put(self.james.eid,age=self.james.age)
        james = Person.index.get_unique("age",'34')
        assert self.james == james
        #Person.remove(self.james.eid,dict(age="34"))


class RelationshipTestCase(unittest.TestCase):

    def setUp(self):
        self.james = Person(name="James", age=34)
        self.julie = Person(name="Julie", age=28)
        self.relationship = Relationship.create(self.james,"knows",self.julie)
        
    def test_properties(self):
        assert self.relationship.label == "knows"
        assert self.relationship.outV._id == self.james.eid
        assert self.relationship.inV._id == self.julie.eid

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NodeTestCase))
    suite.addTest(unittest.makeSuite(RelationshipTestCase))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

