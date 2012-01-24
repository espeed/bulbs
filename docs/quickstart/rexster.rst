Rexster
-------

At it's most basic level, Bulbs is a Python interface to the `Rexster API <https://github.com/tinkerpop/rexster/wiki/Basic-REST-API>`_. 

Rexster is a REST service for graph databases with direct support for searching, ranking, scoring, and more specifically, recommendation. See the `Rexster documenation <https://github.com/tinkerpop/rexster/wiki/>`_ for details.

To use Bulbs, you need to make sure Rexster is up and running.

Start Rexster
^^^^^^^^^^^^^

First, open up a new terminal because we're going to let Rexster run in the foreground.

Then change to the directory where you installed Rexster, and start it with its default configuration::

    $ cd rexster
    $ ./rexster-start.sh

By default, Rexster is configured with a few sample graph databases, including an in-memory TinkerGraph -- this is the database will use for most of these examples.

Browse Rexster
^^^^^^^^^^^^^^

Now check to see that you can browse the TinkerGraph database using these URLs:

* http://localhost:8182
* http://localhost:8182/tinkergraph
* http://localhost:8182/tinkergraph/vertices
* http://localhost:8182/tinkergraph/vertices/1
* http://localhost:8182/tinkergraph/edges
* http://localhost:8182/tinkergraph/edges/8
* http://localhost:8182/tinkergraph/indices
* http://localhost:8182/tinkergraph/indices/vertices?key=name&value=marko

If you can view these, then success! Rexster is up and running.

.. NOTE::

    Rexster returns JSON documents, and Chrome let's you view JSON in
    the browser. However, if you're on Firefox, you may need to
    install the `JSONView
    <https://addons.mozilla.org/en-US/firefox/addon/jsonview/>`_ add
    on; otherwise, Firefox will prompt you to download the file.

Browse DogHouse
^^^^^^^^^^^^^^^

You should also be able to access DogHouse:

* http://localhost:8183
* http://localhost:8183/main/graph/tinkergraph
* http://localhost:8183/main/gremlin/tinkergraph

DogHouse is a browser-based interface to Rexster that allows you to view elements in a graph and simulate a Gremlin-console session. See the `DogHouse documentation <https://github.com/tinkerpop/rexster/wiki/The-Dog-House>`_ for details.

Using DogHouse is sometimes convienent, but most of the time I use the Web browser to browse the JSON documents directly and the external `Gremlin shell <https://github.com/tinkerpop/gremlin/wiki/Using-Gremlin-from-the-Command-Line>`_ to experiment with queries.

Configure Rexster
^^^^^^^^^^^^^^^^^

Configuring Rexster is easy. Simply copy the default rexster.xml and edit it::

   $ cd rexster 
   $ cp src/main/resources/com/tinkerpop/rexster/rexster.xml .
   $ emacs rexster.xml

For example, to configure Rexster to use Neo4j (you don't need to do this now):

#. Open rexster.xml.
#. Copy the <graph> section labeled neo4jsample.
#. Paste it at the top of the <graphs> (plural) section.
#. Change the graph-name to a URL-friendly name you want to reference it by.
#. Set graph-enabled to true. 
#. Set graph-file to the directory where you want to store Neo4j.
#. Configure the remaining parameters as desired (this is not required).
#. Save and close rexster.xml.

See the `Rexster configuration page <https://github.com/tinkerpop/rexster/wiki/Rexster-Configuration>`_ for details.

Here's how to start Rexster using your custom configuration::

   $ ./rexster-start.sh -c rexster.xml

