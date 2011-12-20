from bulbs.writer import ScriptWriter

def create_and_index_vertex(index_name,data,keys=None):
    # We won't have to do it this way when Gremlin methods are overloaded
    # to accept JSON strings in place of Groovy maps. Issue filed on GitHub.
    s = ScriptWriter()
    s.start_transaction()
    s.add_vertex("v")
    s.set_property_data("v",data)
    s.get_index("i",index_name,"Vertex")
    keys = s.get_keys(data,keys)
    for key, value in data.items():
        if key in keys:
            s.index_put("i",key,value,"v")
    s.end_transaction()
    # put the return statement after end_transaction else it won't commit
    s.return_var("v") 
    script = s.get()
    #print s.display()
    return script
