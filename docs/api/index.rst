.. _api:


Bulbs API
=========
.. title:: Bulbs API Documenation, a Python Framework for Graph Databases
.. rubric:: Open-source Python library for graph databases.
.. snippet:: social

Bulbs supports pluggable backends and currently has bindings for `Neo4j Server <http://neo4j.org/>`_  and `Rexster <http://rexster.tinkerpop.com/>`_. 

Rexster is the Blueprints server and so this means Bulbs supports any Blueprints-enabled graph database, including: Neo4j, InfiniteGraph, OrientDB, Dex, TinkerGraph, and OpenRDF Sail.


Bulbs Core
----------

If you are looking for information on a specific function, class or
method, this part of the documentation is for you.

.. toctree::
   :maxdepth: 3

   graph
   config
   gremlin
   elements
   indices
   models
   properties
   client
   tests

Neo4j Server
------------

.. toctree::
   :maxdepth: 3

   neo4jserver/graph
   neo4jserver/client
   neo4jserver/message
   neo4jserver/indices
   neo4jserver/gremlin
   neo4jserver/cypher
   neo4jserver/batch
   neo4jserver/tests

Rexster
-------

.. toctree::
   :maxdepth: 3

   rexster/graph
   rexster/client
   rexster/indices
   rexster/gremlin
   rexster/batch
   rexster/tests

