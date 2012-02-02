# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
from utils import get_logger
from logging import StreamHandler, DEBUG, INFO, WARNING, ERROR, CRITICAL


class Config(object):
    """
    Configuration options for the Resource.

    :param root_uri: Root URI for the resource.
    :type root_uri: str

    :param username: Username for the resource.
    :type username: str

    :param password: Password for the resource.
    :type password: str

    :param log_level: Log level:  DEBUG, INFO, WARNING, ERROR, or CRITICAL
    :type log_level: int

    :ivar log_handler: Python log handler. Defaults to StreamHandler.
    :type log_handler: logging.Handler

    :ivar id_var: Pretty element ID variable. Defaults to eid.
    :type id_var: str

    :ivar type_var: Element-type variable used in Node models. Defaults to element_type.
    :type type_var: str
    
    :ivar type_var: Label variable used in Relationship models. Defaults to label.
    :type type_var: str

    :ivar type_system: Name of the type system. Defaults to json.
    :type type_system: str
    
    :ivar vertex_autoindex: Name of the vertex autoindex. Defaults to vertices.
    :type vertex_autoindex: str

    :ivar edge_autoindex: Name of the edge autoindex. Defaults to edges.
    :type edge_autoindex: str

    :ivar autoindex: Enable auto indexing. Defaults to True.
    :type autoindex: bool

    """

    def __init__(self,root_uri,username=None,password=None,log_level=ERROR):
        self.root_uri = root_uri
        self.username = username
        self.password = password
        self.log_level = log_level
        self.log_handler = StreamHandler
        self.id_var = "eid"
        self.type_var = "element_type"
        self.label_var = "label"
        self.type_system = "json" 
        self.vertex_autoindex = "vertices"
        self.edge_autoindex = "edges"
        self.autoindex = True
        
        self.set_logger()

    def set_logger(self):
        """Sets or updates the log level and log handler."""
        log = get_logger(__name__)
        log.root.setLevel(self.log_level)
        log.root.addHandler(self.log_handler())

