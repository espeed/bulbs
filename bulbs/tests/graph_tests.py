import unittest

from bulbs.config import Config
from bulbs.property import String
from bulbs.element import VertexProxy, EdgeProxy
from bulbs.model import Node, NodeProxy, Relationship, RelationshipProxy
from bulbs.base.client import Client

from .testcase import BulbsTestCase


# Test Models

class User(Node):

    element_type = "user"

    name = String(nullable=False)
    username = String(nullable=False)
  
class Group(Node):

    element_type = "group"

    name = String(nullable=False)

class Member(Relationship):

    label = "member"
    


class GraphTestCase(BulbsTestCase):

    def test_init(self):
        assert isinstance(self.graph.config, Config)
        assert isinstance(self.graph.client, Client)
        assert isinstance(self.graph.vertices, VertexProxy)
        assert isinstance(self.graph.edges, EdgeProxy)

    def test_add_proxy(self):
        self.graph.add_proxy("users", User)
        self.graph.add_proxy("groups", Group)
        self.graph.add_proxy("members", Member)

        assert isinstance(self.graph.users, NodeProxy)
        assert isinstance(self.graph.groups, NodeProxy)
        assert isinstance(self.graph.members, RelationshipProxy)
        
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(GraphTestCase))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

