.. _client:

Graph Interface
---------------
.. title:: Using Blubs as a Rexster Client Connector

Ok, now the fun part. This will show you how to use Bulbs to connect to Rexster from Python and interact with graph databases.


Create a Graph Object
^^^^^^^^^^^^^^^^^^^^^

By default Bulbs is configured to use TinkerPop, an in-memory database with some preloaded data for testing (the same one you viewed in your browser when you started Rexster).

Here's how you create a graph object, your primary interface to Rexster::

>>> from bulbs.graph import Graph
>>> g = Graph()

If you don't supply an argument to Graph(), the graph object will contain a reference to the default database, which you can change in the Bulbs config file. 


Display Vertices
^^^^^^^^^^^^^^^^

Display all the vertices in the graph::

>>> g.V

This returns a list of dicts containg all the vertices in the graph. 

This method is primarily used for testing because you won't normally want to do this for a large database containing millions (or billions) of vertices.

You can see how many vertices were returned by checking the length of the list::

>>> vertices = g.V
>>> len(vertices)

As you can see, the default TinkerGraph database has been automatically loaded with some test data and contains 6 vertices.


Display Edges
^^^^^^^^^^^^^

Display all the edges in the graph::

>>> g.E

Like g.V, this method is primarily used for testing because you won't normally want to do this for a large database.


Create Vertices and Edges
^^^^^^^^^^^^^^^^^^^^^^^^^
Here is a basic example that creates two :class:`~bulbs.element.Vertex` objects and an :class:`~bulbs.element.Edge` that links them together::

>>> james = g.vertices.create({'name':'James'})
>>> julie = g.vertices.create({'name':'Julie'})
>>> g.edges.create(james,"knows",julie)

Now check to see that the vertices and edge were added to the graph::

>>> g.V
>>> g.E


Look Up Indexed Vertices
^^^^^^^^^^^^^^^^^^^^^^^^

Rexster automatically creates 2 generic indexes for you -- one for vertices and one for edges.

Everytime you create a new vertex, it's automatically added to vertex index and you can look it up by its properties:.

This will return all the vertices that have a "name" property with a value of "marko"::

>>> g.idxV(name="james")

As you can see, the return value is a generator. 

A generator is iterable like a list, but it's more memory friendly because it's not copying the entire list around -- it `lazy loads <http://martinfowler.com/eaaCatalog/lazyLoad.html>`_ items as needed::

>>> vertices = g.idxV(name="james")
>>> for vertex in vertices: print vertex

To convert a generator into a :class:`list`, do something like this::

>>> vertices = g.idxV(name="james")
>>> list(vertices)

Notice this list contains a :class:`~bulbs.element.Vertex` object instead of a :class:`dict` like g.V returns.

By default idxV() will return a list of initialized :class:`~bulbs.element.Vertex` objects, but you can tell it not to and get the raw :class:`~bulbs.rest.Response` object by setting raw=True::

>>> resp = g.idxV(name="james",raw=True)
>>> list(resp.results)

resp.results is an iterator (:func:`iter`, which is like a :class:`generator`) containing dicts.


Look Up Indexed Edges
^^^^^^^^^^^^^^^^^^^^^

Likewise everytime you create a new edge, it's automatically added to the edge index and you can look it up by its properties.

This will return all the edges that have the label "created"::

>>> edges = g.idxE(label="knows")
>>> list(edges)

By default idxE() will return a list of initialized :class:`~bulbs.element.Edge` objects, but you can tell it not to and get the raw :class:`~bulbs.rest.Response` object by setting raw=True::

>>> resp = g.idxE(label="knows",raw=True)
>>> list(resp.results)

resp.results is an iterator (:func:`iter`, which is like a :class:`generator`) containing dicts.

.. NOTE:: In normal code, you won't be converting the iterators and genertors to lists -- you'll just iterate over the returned object. I'm converting them to lists here so you can see what they contain.  

.. NOTE:: g.V and g.E don't return initialized objects because they're primarily used for testing so it's more useful to see the raw results.

Get Vertex by ID
^^^^^^^^^^^^^^^^

.. code-block:: python

>>> james._id
3 
>>> james2 = g.vertices.get(3)
>>> assert james == james2


Update Vertex
^^^^^^^^^^^^^

::

>>> g.vertices.update(3, {'age':'34'})


Get Adjacent Edges
^^^^^^^^^^^^^^^^^^

::

>>> james.outE()
>>> james.inE()
>>> james.bothE()


Get Adjacent Vertices
^^^^^^^^^^^^^^^^^^^^^

::

>>> james.outV()
>>> james.inV()
>>> james.bothV()


Connect to Multiple Databases
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To connect to a database other than the default specified in the Bulbs config file, pass in a URL argument pointing to the desired Rexster database::

>>> from bulbs.graph import Graph
>>> default_graph = Graph()
>>> g = Graph('http://localhost:8182/gratefulgraph')

To make sure it's working, try displaying all of the graph's vertices::

>>> g.V

You can configure a new database by modifying Rexster's config file (rexster.xml), which is located under the directory where you installed Rexster.

