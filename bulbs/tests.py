from bulbs.model import Node, NodeProxy, Relationship, RelationshipProxy
from bulbs.property import Integer, String, DateTime
#from bulbs.utils import current_datetime

import bulbs.utils as utils

from bulbs.neo4jserver import Graph

class Example(Node):

    element_type = "example"

    name = String(nullable=False)
    timestamp = DateTime(default=utils.current_datetime)


g = Graph()
g.add_proxy("examples", Example)

james = g.examples.create(name="James")
print james.eid, james.timestamp

