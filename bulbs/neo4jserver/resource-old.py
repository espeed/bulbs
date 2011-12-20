



        
    def create_automatic_vertex_index(self,index_name,element_class,keys=None):
        keys = json.dumps(keys) if keys else "null"
        params = dict(index_name=index_name,element_class=element_class,keys=keys)
        script = self.scripts.get('create_automatic_vertex_index',params)
        print script
        resp = self.gremlin(script)
        print resp.raw
        return resp


    def create_indexed_vertex_automatic(self,data,index_name):
        data = json.dumps(data)
        params = dict(data=data,index_name=index_name)
        script = self.scripts.get('create_automatic_indexed_vertex',params)
        print script
        return self.gremlin(script)

