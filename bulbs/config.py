# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#

import os
#import sys

ENVIRONMENT_VARIABLE = "BULBS_CONFIG"
DATABASE_URL = "http://localhost:8182/graphs/tinkergraph"
SAIL_URL = "http://localhost:8182/graphs/sailgraph"
TYPE_VAR = "element_type"  
MAX_RETRIES = 8
DEBUG = False

config_module = os.environ.get(ENVIRONMENT_VARIABLE,None)
#if not config_module: 
#    msg = "Settings cannot be imported because the environment variable %s is undefined." \
#        % ENVIRONMENT_VARIABLE
#    raise ImportError(msg)
try:
    mod = __import__(config_module, globals(), {}, [])
    filename = "%s/%s" % (mod.__path__[0],"bulbs_config.py")
    execfile(filename)
except Exception:
    # We catch any Exception because the user could do all sorts
    # of things wrong in the import. We can't even guarantee that
    # an ImportError comes from our __import__ call and not an import
    # attempt inside the config file without delving into the backtrace
    # using the traceback module.
    print "Unable to import your local config file. Using default settings."
    #raise

