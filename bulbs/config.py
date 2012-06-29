# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
import os
from .utils import get_logger, urlparse
from logging import StreamHandler, DEBUG, INFO, WARNING, ERROR, CRITICAL

log = get_logger(__name__)


class Config(object):
    """
    Configuration options for Bulbs.

    :param root_uri: Root URI of the database.
    :type root_uri: str

    :param username: Optional username. Defaults to None.
    :type username: str

    :param password: Optional password. Defaults to None.
    :type password: str

    :ivar root_uri: Root URI of the server.
    :ivar username: Optional username. Defaults to None.
    :ivar password: Optional password. Defaults to None.
    :ivar log_level: Python log level. Defaults to ERROR.
    :ivar log_handler: Python log handler. Defaults to StreamHandler.
    :ivar id_var: Name of the element ID variable. Defaults to "eid".
    :ivar type_var: Name of the type variable. Defaults to "element_type".
    :ivar label_var: Name of the label variable. Defaults to "label".
    :ivar type_system: Name of the type system. Defaults to "json".
    :ivar vertex_index: Name of the vertex index. Defaults to "vertex". 
    :ivar edge_index: Name of the edge index. Defaults to "edge". 
    :ivar autoindex: Enable auto indexing. Defaults to True.

    Example:

    >>> from bulbs.config import Config, DEBUG
    >>> from bulbs.neo4jserver import Graph, NEO4J_URI
    >>> config = Config(NEO4J_URI, username="james", password="secret")
    >>> config.set_logger(DEBUG)
    >>> g = Graph(config)

    """

    def __init__(self, root_uri, username=None, password=None):
        self.root_uri = root_uri
        self.username = username
        self.password = password
        self.log_level = ERROR
        self.log_handler = StreamHandler
        self.id_var = "eid"
        self.type_var = "element_type"
        self.label_var = "label"
        self.type_system = "json" 
        self.vertex_index = "vertex"
        self.edge_index = "edge"
        self.autoindex = True
        
        # Set the default log level and log handler
        self.set_logger(self.log_level, self.log_handler)

        # Sanity checks...
        assert self.root_uri is not None

    # TODO: fix duplicate log issue from setting logger multiple times
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
        self.log_level = log_level 
        if log_handler is not None:
            log.root.addHandler(log_handler())

    def set_neo4j_heroku(self, log_level=ERROR, log_handler=None):
        """
        Sets credentials if using the Neo4j Heroku Add On.

        :param log_level: Python log level. Defaults to ERROR.
        :type log_level: int

        :param log_handler: Python log handler. Defaults to log_handler.
        :type log_handler: logging.Handler

        :rtype: None

        """
        url = os.environ.get('NEO4J_REST_URL', None)
        log.debug("NEORJ_REST_URL: %s", url)

        if url is not None:
            parsed =  urlparse(url)
            pieces = (parsed.scheme, parsed.hostname, parsed.port, parsed.path)
            self.root_uri = "%s://%s:%s%s" % pieces
            self.username = parsed.username
            self.password = parsed.password
            self.set_logger(log_level, log_handler)
            log.debug("ROOT_URI: %s", self.root_uri)
            log.debug("USERNAME: %s", self.username)
            log.debug("PASSWORD: %s", self.password)
