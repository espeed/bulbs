
// Index Proxy

def create_vertex_index(index_name) {
  manager = g.index()
  index = manager.forNodes('$index_name')
  // values stored as strings, so keys are stored as json or "null"
  //manager.setConfiguration(index,"keys",$keys)
}
  
def get_vertex_index(index_name) {
  IndexManager manager = g.index()
  Index<Node> index = manager.forNodes(index_name)
  //Map<String, String> config = manager.getConfiguration(index) 
}

// Model Proxy - Vertex
  
// NOTE: Converting all index values to strings because that's what Neo4j does
// anyway, and when using the JSON type system, Rexster doesn't have a way to 
// specify types in the URL for index lookups. This keeps the code consistent.

// TODO: Make this support multiple indices, e.g. an autoindex and a normal index

def create_indexed_vertex(data,index_name,keys) {
  neo4j = g.getRawGraph()
  manager = neo4j.index()
  g.setMaxBufferSize(0)
  g.startTransaction()
  try {
    index = manager.forNodes(index_name)
    vertex = neo4j.createNode()
    for (entry in data.entrySet()) {
      if (entry.value == null) continue;
      vertex.setProperty(entry.key,entry.value)
      if (keys == null || keys.contains(entry.key))
	index.add(vertex,entry.key,String.valueOf(entry.value))
    }
    g.stopTransaction(TransactionalGraph.Conclusion.SUCCESS)
    return vertex
  } catch (e) {
    g.stopTransaction(TransactionalGraph.Conclusion.FAILURE)  
    return e
  }
}


def update_indexed_vertex(_id, data, index_name, keys) {
  vertex = g.getRawGraph().getNodeById(_id)
  manager = g.getRawGraph().index()
  g.setMaxBufferSize(0)
  g.startTransaction()
  try {
    index = manager.forNodes(index_name)
    index.remove(vertex)
    for (String key in vertex.getPropertyKeys())
      vertex.removeProperty(key)
    for (entry in data.entrySet()) {
      if (entry.value == null) continue;
      vertex.setProperty(entry.key,entry.value)
      if (keys == null || keys.contains(entry.key))
	index.add(vertex,entry.key,String.valueOf(entry.value))
    }
    g.stopTransaction(TransactionalGraph.Conclusion.SUCCESS)
    return vertex 
  } catch (e) {
    g.stopTransaction(TransactionalGraph.Conclusion.FAILURE)
    return e
  }
}

// Model Proxy - Edge

def create_indexed_edge(outV,label,inV,data,index_name,keys) {
  import org.neo4j.graphdb.DynamicRelationshipType;
  neo4j = g.getRawGraph()
  manager = neo4j.index()
  vertex = neo4j.getNodeById(outV)
  relationshipType = DynamicRelationshipType.withName(label)
  g.setMaxBufferSize(0)
  g.startTransaction()
  try {
    index = manager.forRelationships(index_name)
    edge = vertex.createRelationshipTo(neo4j.getNodeById(inV),relationshipType)
    for (entry in data.entrySet()) {
      if (entry.value == null) continue;
      edge.setProperty(entry.key,entry.value)
      if (keys == null || keys.contains(entry.key))
	index.add(edge,entry.key,String.valueOf(entry.value))
    }
    g.stopTransaction(TransactionalGraph.Conclusion.SUCCESS)
    return edge
  } catch (e) {
    g.stopTransaction(TransactionalGraph.Conclusion.FAILURE)
    return e
  }
}

def update_indexed_edge(_id, data, index_name, keys) {
  neo4j = g.getRawGraph()
  manager = neo4j.index()
  edge = neo4j.getRelationshipById(_id)
  g.setMaxBufferSize(0)
  g.startTransaction()
  try {
    index = manager.forRelationships(index_name)
    index.remove(edge)
    for (String key in edge.getPropertyKeys())
      edge.removeProperty(key)
    for (entry in data.entrySet()) {
      if (entry.value == null) continue;
      edge.setProperty(entry.key,entry.value)
      if (keys == null || keys.contains(entry.key))
	index.add(edge,entry.key,String.valueOf(entry.value))
    }
    g.stopTransaction(TransactionalGraph.Conclusion.SUCCESS)
    return edge
  } catch (e) { 
    g.stopTransaction(TransactionalGraph.Conclusion.FAILURE)
    return e
  }
}

def index_count(index_name, key, value) {
  index = g.idx(index_name);
  return index.count(key,value);
}



}

// Should this be in the global gremlin library?
// Neo4j requires you delete all adjacent edges first. 
// Blueprints' removeVertex() method does that; the Neo4jServer DELETE URI does not.
def delete_vertex(_id) {
  vertex = g.v(_id)
  g.removeVertex(vertex)
}

