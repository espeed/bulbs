.. _api:


Bulbs API
=========

Bulbs is an open-source Python library and persistence framework for graph 
databases. It connects to `Rexster <http://rexster.tinkerpop.com/>`_, which 
provides access to any Blueprints-enabled graph database, including: 
TinkerGraph, Neo4j, OrientDB, Dex, and OpenRDF Sail.


.. module:: bulbs.neo4jserver.graph

Graph
^^^^^

.. autoclass:: Neo4jGraph
   :members:
   :inherited-members:

.. module:: bulbs.element

Vertices
^^^^^^^^

.. autoclass:: Vertex
   :members:
   :inherited-members:

.. autoclass:: VertexProxy
   :members:
   :inherited-members:

Edges
^^^^^

.. autoclass:: Edge
   :members:
   :inherited-members:

.. autoclass:: EdgeProxy
   :members:
   :inherited-members:


.. module:: bulbs.index

Indices
^^^^^^^

.. autoclass:: Index
   :members:
   :inherited-members:

.. autoclass:: VertexIndexProxy
   :members:
   :inherited-members:

.. autoclass:: EdgeIndexProxy
   :members:
   :inherited-members:


.. module:: bulbs.gremlin

Gremlin
^^^^^^^

.. autoclass:: Gremlin
   :members:
   :inherited-members:

.. module:: bulbs.model

Model
^^^^^^

.. autoclass:: Node
   :members:
   :inherited-members:

.. autoclass:: Relationship
   :members:
   :inherited-members:

.. module:: bulbs.property

Properties
^^^^^^^^^^

.. autoclass:: Property
   :members:
   :inherited-members:

.. autoclass:: String
   :members:
   :inherited-members:

.. autoclass:: Integer 
   :members:
   :inherited-members:

.. autoclass:: Long
   :members:
   :inherited-members:

.. autoclass:: Float
   :members:
   :inherited-members:

.. autoclass:: Null
   :members:
   :inherited-members:

.. autoclass:: List
   :members:
   :inherited-members:

.. autoclass:: Dictionary
   :members:
   :inherited-members:

.. module:: bulbs.resource

Resource
^^^^^^^^

.. autoclass:: Resource
   :members:
   :inherited-members:

Response
^^^^^^^^

.. autoclass:: Response
   :members:
   :inherited-members:

