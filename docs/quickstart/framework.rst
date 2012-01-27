Models
------

Domain Models
^^^^^^^^^^^^^

You can also use Bulbs as a framework to model your domain objects::

    from bulbs.model import Node
    from bulbs.property import Property, String, Integer

    class Person(Node):
        element_type = "person"

        name = Property(String, nullable=False)
        age = Property(Integer)

        def after_created():
            # include code to create relationships and to index the node
            pass

Domain Objects
^^^^^^^^^^^^^^

The framework provides type checking and validatoin to ensure that your 
database properties are stored properly, and you can create "triggers" that 
execute before/after an element is created, read, updated, or deleted.

Here's how you would use the Person model to create domain objects::

    >>> from whybase.person import Person
    >>> from bulbs.model import Relationship
    >>>
    >>> james = Person(name="James Thornton")
    >>> james.eid
    3
    >>> james.name
    'James Thornton'
    >>>
    >>> james = Person.get(3)
    >>> james.age = 34
    >>> james.save()
    >>>
    >>> rush = Person(name="Rush Vann")
    >>>
    >>> Relationship.create(james,"knows",rush)


