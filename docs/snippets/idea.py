from bulbs.model import Node
from bulbs.datatype import Property, String
        
class Idea(Node):

    element_type = "idea"

    text = Property(String, nullable=False)
    stub = Property(String,"make_stub")

    def make_stub(self):
        return utils.create_stub(self.text)
           
    def after_created(self):
        Relationship.create(self,"created_by",current_user)

