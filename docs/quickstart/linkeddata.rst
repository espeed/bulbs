
LinkedData Client
-----------------

Connect to LinkedData Stores
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

And through the OpenRDF sail interface, it can connect to remote `LinkedData 
<https://github.com/tinkerpop/gremlin/wiki/LinkedData-Sail>`_ stores, such as 
DBpedia, Freebase, etc::

>>> from bulbs.graph import Graph
>>> g = Graph(' http://localhost:8182/sailgraph')
>>> v = g.v('http://data.semanticweb.org/person/christian-bizer')

