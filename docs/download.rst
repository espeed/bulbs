.. _download:

.. cssclass:: big 

Download
========
.. title:: Download Bulbs, a Python Framework for Graph Databases
.. rubric:: An open-source Python framework for graph databases.
.. snippet:: social

Bulbs is an open-source Python persistence framework for graph
databases, and it is the first piece of a larger Web-development
toolkit that will be released in the upcoming weeks.

1. Get Bulbs
------------

Bulbs is a Python library. You can install it system wide using the `setuptools <http://pypi.python.org/pypi/setuptools>`_  easy_install utility:

.. code-block:: bash

    $ sudo easy_install bulbs

Or you can install it in your project's `virtual environment <http://www.virtualenv.org/en/latest/>`_ by using `pip <http://pypi.python.org/pypi/pip>`_:

.. code-block:: bash

    $ mkdir whybase
    $ cd whybase
    $ virtualenv env
    $ source env/bin/activate
    (env)$ pip install bulbs

The Bulbs source code is on Github at https://github.com/espeed/bulbs. Feedback welcome. 

See the `Bulbs installation docs </installation>`_ for more details.

2. Get Rexster
--------------

Bulbs connects to Rexster, a `RESTful Web service <http://en.wikipedia.org/wiki/Representational_State_Transfer>`_ for graph databses, and binary bindings are in the works.

To get Rexster, make sure you have `Git <http://git-scm.com/>`_ and `Mavern <http://maven.apache.org/>`_ installed, then do:

.. code-block:: bash

    $ git clone https://github.com/tinkerpop/rexster.git
    $ cd rexster
    $ mvn clean install

This will install Rexster and automatically download embedded versions of the graph databases for you, including `Neo4j <http://neo4j.org/>`_.

See the `Rexster docs <https://github.com/tinkerpop/rexster/wiki>`_ for more details.

3. Get Gremlin
--------------

Gremlin is a `domain-specific language <http://en.wikipedia.org/wiki/Domain-specific_language>`_ for graph databases (like SQL for graphs), and it's what you use to write queries in Bulbs. 

Rexster will automatically install and use an embedded version of Gremlin, but it's nice to have the Gremlin shell installed to experiment with queries. 

To install the Gremlin shell, make sure you have `Git <http://git-scm.com/>`_ and `Maven <http://maven.apache.org/>`_ installed, then do:

.. code-block:: bash

    $ git clone https://github.com/tinkerpop/gremlin.git
    $ cd gremlin
    $ mvn clean install

See the `Gremlin docs <https://github.com/tinkerpop/gremlin/wiki>`_ for more details.

What's Next?
------------

After you download and install Bulbs, Rexster, and Gremlin, read the `Bulbs docs </docs>`_ for information on how to build something with it.
