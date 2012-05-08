//
// Copyright 2012 James Thornton (http://jamesthornton.com)
// BSD License (see LICENSE for details)
//

// TODO: This will error for property values that are lists.
//       See https://groups.google.com/forum/#!topic/neo4j/sjH2f5dulTQ

// Model - Vertex

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

// Model - Edge

def create_indexed_edge(outV,label,inV,data,index_name,keys,label_var) {
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
    index.add(edge,label_var,String.valueOf(label))
    g.stopTransaction(TransactionalGraph.Conclusion.SUCCESS)
    return edge
  } catch (e) {
    g.stopTransaction(TransactionalGraph.Conclusion.FAILURE)
    return e
  }
}

// don't need to update indexed label, it can't change
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

// Indices
def query_exact_index(index_name, key, query_string) {
  // Neo4jTokens.QUERY_HEADER = "%query%"
  return g.idx(index_name).get(key, Neo4jTokens.QUERY_HEADER + query_string)
}

// Metadata

def get_metadata(key, default_value) {
  neo4j = g.getRawGraph();
  properties = neo4j.getKernelData().properties();
  return properties.getProperty(key, default_value);
}

def set_metadata(key, value) {  
  g.setMaxBufferSize(0)
  g.startTransaction()
  try {
    neo4j = g.getRawGraph();
    properties = neo4j.getKernelData().properties();
    resp = properties.setProperty(key, value);
    g.stopTransaction(TransactionalGraph.Conclusion.SUCCESS)
    return resp
  } catch (e) { 
    g.stopTransaction(TransactionalGraph.Conclusion.FAILURE)
    return e
  }
}

def remove_metadata(key) {
  g.setMaxBufferSize(0)
  g.startTransaction()
  try {
    neo4j = g.getRawGraph();
    properties = neo4j.getKernelData().properties();
    resp = properties.removeProperty(key);
    g.stopTransaction(TransactionalGraph.Conclusion.SUCCESS)
    return resp
  } catch (e) { 
    g.stopTransaction(TransactionalGraph.Conclusion.FAILURE)
    return e
  }
}