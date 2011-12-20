# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#

class Config(object):

    def __init__(self,root_uri,username=None,password=None):
        self.root_uri = root_uri
        self.username = username
        self.password = password
        self.id_var = "eid"
        self.type_var = "element_type"
        self.label_var = "label"
        self.type_system = "json" 
        self.debug = False
        
