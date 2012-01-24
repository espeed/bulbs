
====================
Gremlin for Web Revs
====================
--------------------------------------------------
An introduction to Gremlin for Web Revolutionaries
--------------------------------------------------

This is a paragraph.

1. Overview
2. Something
3. More Stuff

This is some Python code (default)::

    from bulbflow.graph import Graph
    g = Graph()
    g.V


And here is some Groovy:

.. code-block:: groovy

    g = new Neo4jGraph('/tmp/neo4j')

    // calculate basic collaborative filtering for vertex 1
    m = [:]
    g.v(1).out('likes').in('likes').out('likes').groupCount(m)
    m.sort{a,b -> a.value <=> b.value}

    // calculate the primary eigenvector (eigenvector centrality) of a graph
    m = [:]; c = 0;
    g.V.out.groupCount(m).loop(2){c++ < 1000}
    m.sort{a,b -> a.value <=> b.value}

 
And that's it.




