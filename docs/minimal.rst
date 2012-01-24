


A Minimal Application
---------------------

A minimal Bulbs application looks something like this:

snippet

NOTES: 1. Keep the code visible on the page, 2. place a link to download the delcartion, 3. Show how to use python -f to load the declaration file in the interpreter.

Save it as person.py and run it with your Python interpreter.


$ python person.py

So what is this code doing?


First, we import the Bulbs classes Graph and Vertex. Graph is the primary interface to Rexster, and most of your actions go through it. In a graph there are two types of elements -- vertices and edges. 

Vertices are the nodes or objects in the graph and edges are the connections between the vertices. 

We are about to create a Person object so we import Vertex so we can subclass it.

Next, we import the Bubls classes Property, Integer, and String. Rexster enables you to store typed data, and since Python is dynamically typed, we need a way to ensure our data gets stored properly -- the Bulbs type system coerces data to appropriate type when possible and won't let you store a string for a Property specified as an integer.

Then we create our Person class, which is a subclass of Vertex, and at the top of every Vertex class, We specify it's element_type.

In a multi-relational graph, where you can have different types of edges between vertices, you need to be able to identify the type of vertices returned by queries -- storing an item's element_type helps enables us to do that.

Now we get to the heart of class definition -- the Property definitioans. Property graphs store data as a list of key/value pairs, which are called properties. 

So in Bulbs, when we define an attribute as a Property, we are saying that it is going to be stored in the database. As we said, in Rexster properties are typed so our Property definitions speicfy the datatype of each attribute. 

You can also specify constraints. Graph properties don't actually have constraints so these are application-level constraints.

In this example, we set the "not null" constraint on the "name" Property by setting nullable to False. The "age" Property does not have this constraint so you are not required to set the "age" Property.

The last step in this class definition is to call the initialize() methodwhen the object is instantiated. As you can see, the initialize() method takes three arguments: element, eid, and kwds.

Notice that the "element" and "eid" arguments default to None. 

The only time we pass in "element" is when we have just retrieved a vertex's data from the database and we want to initialize it -- we pass in the retrieved element and the initialize() method sets the property values for the Python object.

The only time we pass in "eid" (the element ID) is when we are updating an object that hasn't yet been intialized to as a Python object -- for example, when an element's data is being updated from a Web form. 

But in this example, we are creating a new item so only pass in the Property data we want to save, and in this case, "name" is the only required attribute since we set nullable=False in its Property definition.

Note that you can also pass in non-Property attributes, and they will get initialzed to accordingly. 


