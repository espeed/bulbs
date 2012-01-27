from bulbs.model import Node
from bulbs.property import String
        
class Idea(Node):

    element_type = "idea"

    text = String(nullable=False)
    stub = String("make_stub")

    def make_stub(self):
        return utils.create_stub(self.text)
           
    def after_created(self):
        Relationship.create(self,"created_by",current_user)

