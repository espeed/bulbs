# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
from utils import get_logger
from logging import StreamHandler, DEBUG, INFO, WARNING, ERROR, CRITICAL


class Config(object):
    """
    Configuration options for Resource.

    :param root_uri: Root URI for the server.
    :type root_uri: str

    :param username: Username for the server..
    :type username: str

    :param password: Password for the server.
    :type password: str

    :param log_level: Python log level. Defaults to ERROR.
    :type log_level: int

    :ivar log_handler: Python log handler. Defaults to StreamHandler.
    :type log_handler: logging.Handler

    :ivar id_var: Name of the element ID variable. Defaults to eid.
    :type id_var: str

    :ivar type_var: Name of the element-type variable. Defaults to element_type.
    :type type_var: str
    
    :ivar type_var: Name of the label variable. Defaults to label.
    :type type_var: str

    :ivar type_system: Name of the type system. Defaults to json.
    :type type_system: str
    
    :ivar vertex_index: Name of the vertex autoindex. Defaults to vertices.
    :type vertex_index: str

    :ivar edge_index: Name of the edge autoindex. Defaults to edges.
    :type edge_index: str

    :ivar autoindex: Enable auto indexing. Defaults to True.
    :type autoindex: bool

    """
    def __init__(self,root_uri,username=None,password=None):
        self.root_uri = root_uri
        self.username = username
        self.password = password
        self.log_level = ERROR
        self.log_handler = StreamHandler
        self.id_var = "eid"
        self.type_var = "element_type"
        self.label_var = "label"
        self.type_system = "json" 
        self.vertex_index = "vertices"
        self.edge_index = "edges"
        self.autoindex = True
        
        self.set_logger(self.log_level, self.log_handler)

    def set_logger(self, log_level, log_handler=None):
        """Sets or updates the log level and log handler."""
        log = get_logger(__name__)
        log.root.setLevel(log_level)
        if log_handler is not None:
            log.root.addHandler(log_handler())

 
