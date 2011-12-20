from bulbs.element import Vertex, Edge

class Registry(object):
    
    def __init__(self):
        self.class_map = dict(vertex=Vertex,edge=Edge)
        self.proxy_map = dict()
        self.index_map = dict()
        self.scripts_map = dict()

    # Classes
    def add_class(self,*classes):
        for element_class in classes:
            if element_class not in (Vertex, Edge): 
                # Vertex and Edge are always set by default
                element_type = getattr(element_class,self.type_var)
                self.class_map[element_type] = element_class

    # Proxies
    def add_proxy(self,key,proxy):
        self.proxy_map[key] = proxy

    def get_proxy(self,key):
        return self.proxy_map[key]

    # Indicies
    def add_index(self,key,index):
        self.index_map[key] = index
        
    def get_index(self,key):
        return self.index_map[key]
 
    # Scripts
    def add_scripts(self,key,scripts):
        self.scripts_map[key] = scripts

    def get_scripts(self,key):
        return self.scripts_map[key]
