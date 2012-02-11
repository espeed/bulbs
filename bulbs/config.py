# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
from utils import get_logger
from logging import StreamHandler, DEBUG, INFO, WARNING, ERROR, CRITICAL


class Config(object):
    """
    Configuration options for the Graph object.

    :param root_uri: Root URI of the server.
    :type root_uri: str

    :param username: Optional username. Defaults to None.
    :type username: str

    :param password: Optional password. Defaults to None.
    :type password: str

    Example:

    >>> from bulbs.config import Config, DEBUG
    >>> from bulbs.neo4jserver import Graph, NEO4J_URI
    >>> config = Config(NEO4J_URI, username="james", password="secret")
    >>> config.set_logger(DEBUG)
    >>> g = Graph(config)

    """
    def __init__(self, root_uri, username=None, password=None):

        #: Root URI of the server.
        self.root_uri = root_uri

        #: Optional username. Defaults to None.
        self.username = username

        #: Optional password. Defaults to None.
        self.password = password

        #: Python log level. Defaults to ERROR.
        self.log_level = ERROR

        #: Python log handler. Defaults to StreamHandler.
        self.log_handler = StreamHandler

        #: Name of the element ID variable. Defaults to "eid".
        self.id_var = "eid"

        #: Name of the type variable. Defaults to "element_type".
        self.type_var = "element_type"

        #: Name of the label variable. Defaults to "label".
        self.label_var = "label"

        #: Name of the type system. Defaults to "json".
        self.type_system = "json" 

        #: Name of the vertex index. Defaults to "vertices".
        self.vertex_index = "vertices"

        #: Name of the edge index. Defaults to "edges".
        self.edge_index = "edges"

        #: Enable auto indexing. Defaults to True.
        self.autoindex = True
        
        self.set_logger(self.log_level, self.log_handler)

    def set_logger(self, log_level, log_handler=None):
        """
        Sets or updates the log level and log handler.

        :param log_level: Python log level.
        :type log_level: int

        :param log_handler: Python log handler. Defaults to log_handler.
        :type log_handler: logging.Handler

        :rtype: None

        """
        log = get_logger(__name__)
        log.root.setLevel(log_level)
        if log_handler is not None:
            log.root.addHandler(log_handler())

 
