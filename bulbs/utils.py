# -*- coding: utf-8 -*-
#
# Copyright 2011 James Thornton (http://jamesthornton.com)
# BSD License (see LICENSE for details)
#

def xstr(s):
    return '' if s is None else str(s)

def quote(s):
    s = xstr(s)
    if s:
        s = "'%s'" % (s)
    return s

def initialize_element(class_map,key,result):
    element_class = class_map[key]
    return element_class(result)
 
def element_repr(element):
    if element._type == "vertex":
        return "==>v[%d]" % (element.eid)
    elif element._type == "edge":
        return "==>e[%d][%d-%s->%d]" % \
            (element.eid,element.outV.eid,element.label,element.inV.eid)

def coerce_id(_id):
    # try to coerce the element ID string to an int.
    # ORIENTDB USES STRINGS SO THIS WON'T WORK FOR IT
    try:
        return int(_id)
    except:
        return _id


#def pop_arg(self,args,position,arg_type):
#    value = None
#    args = list(args)
#    if args and isinstance(args[position], arg_type):
#        value = args.pop(position)            
#    return args, value



