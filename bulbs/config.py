# -*- coding: utf-8 -*-
#
# Copyright 2012 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#
from utils import get_logger
from logging import DEBUG, ERROR, StreamHandler


class Config(object):

    def __init__(self,root_uri,username=None,password=None,log_level=ERROR):
        self.root_uri = root_uri
        self.username = username
        self.password = password
        self.id_var = "eid"
        self.type_var = "element_type"
        self.label_var = "label"
        self.type_system = "json" 
        self.vertex_autoindex = "vertices"
        self.edge_autoindex = "edges"
        self.autoindex = True
        self.log_level = log_level
        self.log_handler = StreamHandler
        
        self.configure_logging()

    def configure_logging(self):
        log = get_logger(__name__)
        log.root.setLevel(self.log_level)
        log.root.addHandler(self.log_handler())

