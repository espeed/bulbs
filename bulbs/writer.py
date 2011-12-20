#
# Not In Use
#
class Library(object):

    def __init__(self,resource):
        self.resource = resource

    def create_and_index_vertex(self,data,index,index_keys=None):
        index_data = utils.get_index_data(data,index_keys)
        index_data = json.dumps(index_data)
        data = json.dumps(data)
        params = dict(data=data,index_name=index.index_name,index_data=index_data)
        script = self.resource.scripts.get("create_and_index_vertex",params)
        return self.resource.gremlin(script)
   

class ScriptWriter(object):
    """
    ScriptWriter is an experiment that would be akin to a Python-based 
    Google Web Toolkit (http://code.google.com/webtoolkit/) for 
    building Gremlin scripts. And while it works well, I think it's simpler
    to source Gremlin code from gremlin.yaml. But I'm leaving ScriptWriter
    in the codebase for now so others can experiment with it. - James

    Example:

    def create_indexed_vertex(index_name,data,keys=None):
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
        s.return_var("v")
        return s.get()

    data = dict(name="James",age=34)
    script = create_indexed_vertex("people",data)
    resp = self.resource.gremlin(script)
    """
    
    def __init__(self):
        self.lines = []

    def __add__(self,line):
        self.lines.append(line)

    # Elements
    def add_vertex(self,varname):
        line = "Vertex %s = g.addVertex()" % (varname)
        self.lines.append(line)

    def add_edge(self,varname,outV,label,inV):
        line  = "Edge %s = g.addEdge(null,%s,%s,%s)" % (varname,outV,inV,label)
        self.lines.append(line)

    def set_property(self,element,key,value):
        line = "%s.setProperty('%s',%s)" % (element,key,self.quote(value))
        self.lines.append(line)

    def set_property_data(self,element,data):
        for key, value in data.items():
            self.set_property(element,key,value)

    # Indices
    def get_index(self,varname,index_name,index_class):
        line = "%s = g.getIndex('%s',%s)" % (varname, index_name,index_class)
        self.lines.append(line)

    def index_put(self,index,key,value,element):
        line = "%s.put('%s',%s,%s)" % (index,key,self.quote(value),element)
        self.lines.append(line)

    def index_get(self,index,key,value):
        line = "%s.get('%s',%s,%s)" % (index,key,self.quote(value))
        
    def index_remove(self,index,key,value,element):
        line = "%s.remove('%s',%s,%s)" % (index,key,self.quote(value),element)
        self.lines.append(line)

    # Graph
    def return_var(self,varname):
        self.lines.append("return %s" % varname)

    def start_transaction(self,buffer_size=0):
        self.lines.append("g.setMaxBufferSize(%d)" % buffer_size)
        self.lines.append("g.startTransaction()")
        
    def end_transaction(self):
        self.lines.append("g.stopTransaction(TransactionalGraph.Conclusion.SUCCESS)")

    # Script Methods
    def append(self,script):
        self.lines.append(script)

    def get(self):
        script = ";".join(self.lines)
        return script

    def display(self):
        script = ";\n".join(self.lines)
        print script

    def compile(self):
        # store pre-compiled tempaltes in config?
        pass

    # Utils
    def quote(self,value):
        # quote it if it's a string, set to null if None, else return the value
        if type(value) == str:
            value = "'%s'" % value
        elif value is None:
            value = "null"
        return value

    def get_keys(self,data,keys):
        if not keys:
            keys = data.keys()
        return keys

