.. _overview:

.. cssclass:: big 


Overview
========
.. title:: Overview of Bulbs, a Python Framework for Graph Databases
.. rubric:: A Python framework for graph databases. 
.. snippet:: social

Bulbs is an open-source Python persistence framework for graph
databases and the first piece of a larger Web-development toolkit that
will be released in the upcoming weeks.

It's like an ORM for graphs, but instead of SQL, you use the
graph-traveral language `Gremlin <http://gremlin.tinkerpop.com>`_ to
query the database.

You can use it to connect to `Neo4j Server <http://neo4j.org/>`_ or `Rexster 
<http://rexster.tinkerpop.com>`_, which allows you to connect to 
any `Blueprints <https://github.com/tinkerpop/blueprints/wiki/>`_-enabled
database, including also `OrientDB
<http://www.orientechnologies.com/orient-db.htm>`_, `Dex
<http://www.sparsity-technologies.com/dex>`_, and `OpenRDF
<http://www.openrdf.org/>`_  (and there is an `InfiniteGraph
implementation
<http://blog.infinitegraph.com/2011/02/04/infinitegraph-announces-release-1-1-with-new-indexing-options-and-improved-performance/>`_ in development).  

This means your code is portable because you can to plug into different graph 
database backends without worrying about vendor lock in.

Bulbs was developed in the process of building `Whybase
<http://whybase.com/>`_, a startup that will open for preview this
fall. Whybase needed a persistence layer to model its complex
relationships, and Bulbs is an open-source version of that framework.

You can use Bulbs from within any Python Web-development framework,
including `Flask <http://flask.pocoo.org/docs/>`_, `Pyramid
<http://docs.pylonsproject.org/docs/pyramid.html>`_, and `Django
<https://www.djangoproject.com>`_.

Code Example
------------

Here's how you model domain objects:

.. literalinclude:: snippets/idea.py

And here's how you create domain objects:

.. code-block:: pycon

    >>> from whybase.idea import Idea
    >>> idea = Idea(text="the key to life is perspective")
    >>> idea.eid
    >>> 8
    >>> idea.text
    'the key to life is perspetive'
    >>> idea.stub
    'the-key-to-life-is-perspective'

Why Graphs?
-----------

Graph are a much more elegant way of storing relational data. Graphs are a fundamental data structure in computer science,  and with graph databases you don't have to mess with tables or joins -- everything is explicitly joined.

For tabular data, relational databases rock. But the relational model doesn't align well with object-orientated programming so you have an ORM layer that adds complexity to your code. And with relational databases, the complexity of your schema grows with the complexity of the data.

The graph-database model simplifies much of this and makes working with the modern-day social graph so much cleaner. Graphs allow you to do powerful things like find inferences inside the data in ways that would be hard to do with a relational database.

While you can model a graph in a relational database, anything that's not a real graph database require an external index lookup for each traversal step. With graph databases, each node carries a local set of indices of its adjacent nodes, and in large-scale traversals, bypassing the external index lookup allows your queries to run much faster.

Emerging Landscape
------------------

Some really power tools are beginning to emerge in this space.

Neo4j is an open-source graph database that can
contain `32 billion nodes
<http://blog.neo4j.org/2011/03/neo4j-13-abisko-lampa-m04-size-really.html>`_
and traverse `2 million relationships per second
<http://www.infoq.com/news/2010/02/neo4j-10>`_ on conventional
hardware. It has been tested in production for over 10 years, and the
community edition is now free. 

You can `download Neo4j <http://neo4j.org/download/>`_ or connect to it via the `Neo4j Heroku Add On <http://addons.heroku.com/neo4j>`_.

Traversing graphs has been made simple by `Gremlin <https://github.com/tinkerpop/gremlin/wiki>`_, a wonderfully expressive, Turing-complete graph-programming language.

Gremlin is a `domain-specific language <http://en.wikipedia.org/wiki/Domain-specific_language>`_ for graph databases (like SQL for graphs), and it's what you use to write queries in Bulbs. With Gremlin, you can do stuff like calculate PageRank in 2 lines.

Gremlin Screencast
------------------

To see the power of Gremlin, watch this 8 minute screencast by its creator,
`Marko Rodriguez <http://markorodriguez.com/>`_:

.. raw:: html

    <iframe width="640" height="390"
    src="http://www.youtube.com/embed/5wpTtEBK4-E" frameborder="0"
    allowfullscreen></iframe>


 
Download Bulbs
--------------

Go to the `download page </download>`_ for info on how to download Bulbs.
