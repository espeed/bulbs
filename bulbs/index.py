from element import Vertex, Edge, get_base_type

class IndexProxy(object):
    """
    An interface for interacting with indices on Rexster.

    :param resource: The Resource object for the database.
    :param index_class: The index class for this proxy, e.g. RexsterIndex.

    """

    def __init__(self,index_class,resource):
        self.index_class = index_class
        self.resource = resource
                        
    def create(self,index_name,element_class,*args,**kwds):
        """ 
        Adds an index to the database and returns it. 

        index_keys must be a string in this format: '[k1,k2]'
        Don't pass actual list b/c keys get double quoted.

        :param index_name: The name of the index to create.

        :param index_class: The class of the elements stored in the index. 
                            Either vertex or edge.
        
        """
        create_index = self._get_create_method(element_class)
        resp = create_index(index_name,*args,**kwds)
        index = self.index_class(self.resource,resp.results)
        self.register(index_name,index)
        return index

    def get(self,index_name,element_class):
        """Returns the Index object with the specified name or None if not found."""
        get_method = self._get_get_method(element_class)
        resp = get_method(index_name)
        if resp.results:
            index = self.index_class(self.resource,resp.results)
            self.register(index_name,index)
            return index

    def get_or_create(self,index_name,element_class,**kwds):
        # get it, create if doesn't exist, then register it
        index = self.get(index_name,element_class)
        if not index:
            index = self.create(index_name,element_class,**kwds)
        return index

    def delete(self,index_name):
        """Deletes/drops an index and returns the Rexster Response object."""
        resp = self.resource.delete_index(index_name)
        return resp

    def register(self,index_name,index):
        self.resource.registry.add_index(index_name,index)


    def _get_create_method(self,element_class):
        method_map = dict(vertex=self.resource.create_vertex_index,
                          edge=self.resource.create_edge_index)
        base_type = get_base_type(element_class)
        create_method = method_map.get(base_type)
        return create_method

    def _get_get_method(self,element_class):
        method_map = dict(vertex=self.resource.get_vertex_index,
                          edge=self.resource.get_edge_index)
        base_type = get_base_type(element_class)
        get_method = method_map.get(base_type)
        return get_method
