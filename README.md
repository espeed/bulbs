# Bulbs

_a Python persistence framework for graph databases_


## What is Bulbs?

Bulbs is a Python persistence framework for graph databases that supports
Python 3 and Python 2.7 originally created by James Thornton.

It connects to several graph-database servers, including Neo4j Server and Rexster.

Neo4j Server is Neo4j's open-source REST server, and it is available as an
[Heroku Add On](http://addons.heroku.com/neo4j).

Rexster is a graph-database REST server optimized for recommendations.
It is part of the  TinkerPop stack and connects to any Blueprints-enabled
graph database, including Neo4j, OrientDB, Dex, OpenRDF Sail, and TinkerGraph.

Bulbs supports pluggable back ends, and more native bindings are in the works.

## Is it ready?

A preview release is out now, and I welcome feedback on how to improve it.
The API will probably change somewhat until we hit 1.0.

## What do I need?

* [Neo4j Server](http://neo4j.org/), or
* [Rexster](https://github.com/tinkerpop/rexster)

And a few Python libraries, such as ujson and httplib2.

## Where are the docs?

The 0.3.x docs are now online at [Bulbflow.org](http://bulbflow.org).


* [Bulbs Overview on StackOverflow](http://stackoverflow.com/tags/bulbs/info)
* [Customizing Bulbs Models Example](http://stackoverflow.com/a/16764036/161085)
* [Overview on Bulbs' Design](http://stackoverflow.com/a/15358024/161085)

## Where can I get help?

* [Neo4j User group](https://groups.google.com/forum/#!forum/neo4j)
* [Gremlin User group](https://groups.google.com/forum/#!forum/gremlin-users)
* Email me directly at james@jamesthornton.com.
