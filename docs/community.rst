.. cssclass:: big 

Community
=========
.. title:: The Bulbs Community, a Python Framework for Graph Databases
.. rubric:: The graph-database ecosystem is growing fast. 
.. snippet:: social


Here a few places to check out.

TinkerPop
---------

`TinkerPop <http://www.tinkerpop.com/>`_ is a developers group that
has built much of the open-source software stack for the emerging
graph database landscape. It was co-founded by `Marko Rodriguez
<http://markorodriguez.com/>`_, the creator of Rexster, Gremlin,
Pipes, Frames, and Blueprints.

`Rexster <https://github.com/tinkerpop/rexster/wiki/>`_ is a REST
server that sits on top of the TinkerPop stack, and `Stephen Mallette
<https://github.com/spmallette>`_ is one of its primary
contributors. Because Bulbs connects to Rexster, by using Bulbs, you
get access to everything TinkerPop provides:


.. image:: http://media.tumblr.com/tumblr_ljp63oHWaG1qa7x40.png
   :target: http://www.tinkerpop.com
   :align: center 

`Blueprints <https://github.com/tinkerpop/blueprints/wiki/>`_ provides
the foundation and a common interface to graph databases, which means
your code is portable because you can to plug into different graph
database backends without worrying about vendor lock in.

Here are some graph databases that have Blueprints implementations:

* TinkerGraph
* Neo4j 
* Sail
* OrientDB 
* Dex 
* InfiniteGraph (`currently in development <http://blog.infinitegraph.com/2011/02/04/infinitegraph-announces-release-1-1-with-new-indexing-options-and-improved-performance/>`_)

The `Gremlin Users Group
<https://groups.google.com/forum/#!forum/gremlin-users>`_ is the
primary discussion forum for anything related to the TinkerPop stack,
including Gremlin, Rexster and graph databases in general (go here
first).

HansanB made `this comment <https://groups.google.com/d/msg/gremlin-users/pF577035UpY/M7t9uIiIOtIJ>`_ the other day comparing TinkerPop to the how it was in the early days of JServ/Tomcat::

    Something like 13 yrs ago, I was trying to do server-side Java.  It 
    was a nightmare, until I discovered a thing called Apache JServ. 

    It was simple, elegant and the developer group was wonderfully 
    supportive and well organized. 

    Just as with JServ, way back then, Tinkerpop has all the same 
    characteristics, and gives me the same feeling of having hit on 
    something really valuable that will take me a long way. 

    Well ...  JServ morphed into TomCat, and I've used it consistently
    ever since.  I'm confident Tinkerpop is going the same way, so I'm
    only too pleased to help where I can.

    Sincerest regards, 
    Hasan 

To get a feel for graphs, watch these videos by Marko: 

* `Gremlin: A Graph Traversal Language (Tutorial 1) <http://www.youtube.com/watch?v=5wpTtEBK4-E>`_
* `The Graph Traversal Programming Pattern <http://vimeo.com/13213184>`_


Neo4j
----

`Neo4j <http://neo4j.org/>`_ is one of the leading open-source graph
databases. The `Community Edition is now free
<http://blogs.neotechnology.com/emil/2011/04/graph-databases-licensing-and-mysql.html>`_,
and it can store `32 billion nodes
<http://blog.neo4j.org/2011/03/neo4j-13-abisko-lampa-m04-size-really.html>`_
while traversing `2 million nodes per second
<http://www.infoq.com/news/2010/02/neo4j-10>`_.


`Peter Neubauer <https://twitter.com/#!/peterneubauer>`_ is a Neo4j
co-founder and also a co-founder of TinkerPop. You can check out the
entire `Neo4j team <https://github.com/neo4j>`_ on Github.

When you ask a question on the `Neo4j mailing list
<http://neo4j.org/community/feeds/>`_, you usually get a response
within a few minutes.


Watch this `video on Neo4j <http://www.youtube.com/watch?v=2ElGO1P8v0c>`_ for quick overview.


OrientDB
--------

`OrientDB <http://www.orientechnologies.com/>`_ is an open-source
graph database getting ready to release it's 1.0.

`Luca Garulli <http://www.orientechnologies.com/luca-garulli.htm>`_ is
the project lead, and active discussions are always going on at the
`OrientDB discussion group
<https://groups.google.com/forum/#!forum/orient-database>`_.
 
Dex
---

`Dex <http://www.sparsity-technologies.com/dex>`_ is a graph database
that originated at the Data Management group at the Polytechnic
University of Catalonia (DAMA-UPC). It was spun-off into
Sparsity-Technologies in March 2010.

There's a free community version for academic or evaluation purposes
`available for download
<http://www.sparsity-technologies.com/dex_downloads>`_. The free
version is limited to 1 million nodes, but there is no limit on edges.

OpenRDF
-------

`OpenRDF <http://www.openrdf.org/>`_ is the home for Sesame and
related applications.

Sesame is the "de-facto standard framework for processing RDF data."
It provides an easy-to-use API that can be connected to most of the
leading RDF data stores.

You can subscribe to the `Sesame mailing list
<http://www.openrdf.org/community.jsp>`_ here.
