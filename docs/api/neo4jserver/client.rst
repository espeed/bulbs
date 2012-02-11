.. _neo4j_client:

Neo4j Server: Client
======================
.. title:: Bulbs API: Neo4j Server: Client
.. rubric:: Bulbs low-level API for Neo4j Server.
.. snippet:: social

Example:

>>> from bulbs.config import Config
>>> from bulbs.neo4jserver import Neo4jClient, NEO4J_URI
>>> config = Config(NEO4J_URI)
>>> client = Neo4jClient(config)
>>> script = client.scripts.get("get_vertices")
>>> response = client.gremlin(script, params=None)
>>> result = response.results.next()

.. module:: bulbs.neo4jserver.client


Constants
---------

.. data:: NEO4J_URI

   The server's default root URI (http://localhost:7474/db/data/).

Neo4jClient
-------------

.. autoclass:: Neo4jClient
   :members:
   :inherited-members:

Neo4jRequest
-------------

.. autoclass:: Neo4jRequest
   :members:
   :inherited-members:

Neo4jResponse
-------------

.. autoclass:: Neo4jResponse
   :members:
   :inherited-members:


Neo4jResult
-----------

.. autoclass:: Neo4jResult
   :members:
   :inherited-members:
