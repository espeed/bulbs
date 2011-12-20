from bulbs.typesystem import TypeSystem
from bulbs.property import String, Integer, Float, Null, List, Dictionary


class RexsterTypeSystem(TypeSystem):
    
    content_type="application/json"

    def add_db_mappings(self):
        # Rexster types
        self.type_map['string'] = String
        self.type_map['integer'] = Integer
        self.type_map['float'] = Float
        self.type_map['list'] = List
        self.type_map['map'] = Dictionary
        self.type_map['array'] = List

    #def to_db(self,data):
    #    datatype = type(data)
    #    value = data
    #    klass = self.type_map[datatype]
    #    return klass.to_db(self,value)

    # Property Conversions
    def string_to_db(self,value):
        return '(string,%s)' % (value)

    def integer_to_db(self,value):
        return '(integer,%d)' % (value)
    
    def long_to_db(self,value):
        return '(long,%d)' % (value)

    def float_to_db(self,value):
        return '(float,%f)' % (value)

    def null_to_db(self,value):
        return '(string,%s)' % (value)

    def list_to_db(self,value):
        val_list = []
        for item in value:
            val_list.append(self.to_db(item))
        return "(list,(%s))" % (','.join(val_list))    

    def dictionary_to_db(self,value):
        pair_list = []
        for k,v in value.items():
            pair = "%s=%s" % (k,self.to_db(v))
            pair_list.append(pair)
        return "(map,(%s))" % (','.join(pair_list))    

    #self.to_db.map = dict()
    #self.to_db_map.update({str:self.string_to_db})
    #self.to_db_map.update({int:self.integer_to_db})
    #self.to_db_map.update({long:self.long_to_db})
    #self.to_db_map.update({float:self.float_to_db})
    #self.to_db_map.update({list,self.list_to_db})
    #self.to_db_map.update({dict,self.dict_to_db})
    #self.to_db_map.update({type(None),self.null_to_db})
        

