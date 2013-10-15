// NOTE: Converting all index values to strings because that's what Neo4j does
// anyway, and when using the JSON type system, Rexster doesn't have a way to 
// specify types in the URL for index lookups. This keeps the code consistent.

// using closures for clarity

// TODO: Make this support multiple indices, e.g. an autoindex and a normal index


// Model Proxy - Vertex

def create_indexed_vertex(data,index_name,keys) {
  def createIndexedVertex = {
    vertex = g.addVertex()
    index = g.idx(index_name)
    for (entry in data.entrySet()) {
      if (entry.value == null) continue;
      vertex.setProperty(entry.key,entry.value)
      if (keys == null || keys.contains(entry.key))
	index.put(entry.key,String.valueOf(entry.value),vertex)
    }
    return vertex
  }
  def transaction = { final Closure closure ->
    try {
      results = closure();
      g.commit();
      return results; 
    } catch (e) {
      g.rollback();
      throw e;
    }
  }
  return transaction(createIndexedVertex);
}


def update_indexed_vertex(_id, data, index_name, keys) {
  def updateIndexedVertex = { 
    vertex = g.v(_id);
    index = g.idx(index_name);
    // remove vertex from index
    for (String key in vertex.getPropertyKeys()) {
      if (keys == null || keys.contains(key)) {
	value = vertex.getProperty(key);
	index.remove(key, String.valueOf(value), vertex);
      }
    }
    ElementHelper.removeProperties([vertex]);
    ElementHelper.setProperties(vertex,data);
    // add vertex to index
    for (entry in data.entrySet()) {
      if (entry.value == null) continue;
      if (keys == null || keys.contains(entry.key))
	index.put(entry.key,String.valueOf(entry.value),vertex);
    }    
    return vertex;
  }
  def transaction = { final Closure closure ->
    try {
      results = closure();
      g.commit();
      return results; 
    } catch (e) {
      g.rollback();
      throw e;
    }
  }
  return transaction(updateIndexedVertex);
}


// Model Proxy - Edge

def create_indexed_edge(outV,label,inV,data,index_name,keys,label_var) {
  def createIndexedEdge = {
    index = g.idx(index_name)
    edge = g.addEdge(g.v(outV),g.v(inV),label)
    for (entry in data.entrySet()) {
      if (entry.value == null) continue;
      edge.setProperty(entry.key,entry.value)
      if (keys == null || keys.contains(entry.key))
	index.put(entry.key,String.valueOf(entry.value),edge)
    }
    index.put(label_var,String.valueOf(label),edge)
    return edge
  }
  def transaction = { final Closure closure ->
    try {
      results = closure();
      g.commit();
      return results; 
    } catch (e) {
      g.rollback();
      throw e;
    }
  }
  return transaction(createIndexedEdge);
}

// don't need to update indexed label, it can't change
def update_indexed_edge(_id, data, index_name, keys) {
  def updateIndexedEdge = {
    edge = g.e(_id);
    index = g.idx(index_name);
    for (String key in edge.getPropertyKeys()) {
      if (keys == null || keys.contains(key)) {
	value = edge.getProperty(key)
	index.remove(key, String.valueOf(value), edge);
      }
    }
    ElementHelper.removeProperties([edge]);
    ElementHelper.setProperties(edge,data);
    for (entry in data.entrySet()) {
      if (entry.value == null) continue;
      if (keys == null || keys.contains(entry.key))
	index.put(entry.key,String.valueOf(entry.value),edge)
    return edge;
    }
  }
  def transaction = { final Closure closure ->
    try {
      results = closure();
      g.commit();
      return results; 
    } catch (e) {
      g.rollback();
      throw e;
    }
  }
  return transaction(updateIndexedEdge);
}
