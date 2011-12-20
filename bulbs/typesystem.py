from bulbs.property import String, Integer, Float, Null, List, Dictionary


class TypeSystem(object):
    
    content_type = None
    type_map = dict()

    # Subclass this to add the DB types

    def __init__(self):
        self.add_python_mappings()
        self.add_db_mappings()

    def add_python_mappings(self):
        self.type_map[str] = String
        self.type_map[int] = Integer
        self.type_map[float] = Float
        self.type_map[list] = List
        self.type_map[dict] = Dictionary
        self.type_map[type(None)] = Null

    def add_db_mappings(self):
        pass

    def to_python(self,value,datatype):
        # TODO: warn or log errors
        try: return datatype(value)
        except: return None

    def to_db(self,data):
        datatype = type(data)
        value = data
        klass = self.type_map[datatype]
        return klass.to_db(self,value)

    #def convert(self,value,datatype):
    #    # TODO: warn or log errors
    #    try: return datatype(value)
    #    except: return None
            
    # To Python
    def string_to_python(self,value):
        return self.to_python(value,str)

    def integer_to_python(self,value):
        return self.to_python(value,int)

    def long_to_python(self,value):
        return self.to_python(value,long)

    def float_to_python(self,value):
        return self.to_python(value,float)              

    def null_to_python(self,value):
        return None

    def list_to_python(self,value):
        val_list = []
        for item in value:
            val_list.append(self.to_python(item))
        return val_list

    def dictionary_to_python(self,value):
        dict_ = {}
        for k,v in value.items():
            dict_.update({k:self.to_python(v)})
        return dict_

    # To DB
    def string_to_db(self,value):
        return value

    def integer_to_db(self,value):
        return value
    
    def long_to_db(self,value):
        return value

    def float_to_db(self,value):
        return value

    def null_to_db(self,value):
        # Neo4j doesn't allow null values for properties
        # so we have to use an empty string.
        return ""

    def list_to_db(self,value):
        return value

    def dictionary_to_db(self,value):
        return value


class JSONTypeSystem(TypeSystem):

    content_type = "application/json"
