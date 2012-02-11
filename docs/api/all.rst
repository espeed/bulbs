.. _api:


Bulbs API
=========
.. rubric:: Open-source Python library for graph databases.
.. raw:: html 
   :file: social

Bulbs supports pluggable backends and currently has bindings for `Neo4j Server <http://neo4j.org/>`_  and `Rexster <http://rexster.tinkerpop.com/>`_. 

Rexster is the Blueprints server and so this means Bulbs supports any Blueprints-enabled graph database, including: Neo4j, InfiniteGraph, OrientDB, Dex, TinkerGraph, and OpenRDF Sail.

.. module:: bulbs.graph

Graph
^^^^^

.. autoclass:: Graph
   :members:
   :inherited-members:


.. module:: bulbs.config

Config
^^^^^^
.. autoclass:: Config
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
   
   .. autoattribute:: _outV
   .. autoattribute:: _inV

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

.. module:: bulbs.model


Nodes
^^^^^

.. autoclass:: Node
   :members:
   :inherited-members:

.. autoclass:: NodeProxy
   :members:
   :inherited-members:

Relationships
^^^^^^^^^^^^^

.. autoclass:: Relationship
   :members:
   :inherited-members:

.. autoclass:: RelationshipProxy
   :members:
   :inherited-members:


.. module:: bulbs.property

Properties
^^^^^^^^^^

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


.. module:: bulbs.gremlin

Gremlin
^^^^^^^

.. autoclass:: Gremlin
   :members:
   :inherited-members:


.. module:: bulbs.client

Client
^^^^^^

.. autoclass:: Client
   :members:
   :inherited-members:

Response
^^^^^^^^

.. autoclass:: Response
   :members:
   :inherited-members:

