//
// NOTE: Using groovy scripts like this won't work until Rexster
//       implements the "params" bindings. Until then we'll have
//       to use gremlin.yaml templates and do variable substitution. 
//
//       Gremlin scripts are in gremlin.yaml.
//
//       See https://github.com/tinkerpop/rexster/issues/143 and
//           https://github.com/tinkerpop/rexster/issues/146 
//           



//
// Examples from Neo4j's gremlin.groovy
//
def create_indexed_vertex(data,index_name,keys) {
  manager = g.getRawGraph().index()
  index = manager.forNodes(index_name)
  g.setMaxBufferSize(0)
  g.startTransaction()
  vertex = g.getRawGraph().createNode()
  for (entry in data.entrySet()) {
    if (entry.value == null) continue;
      vertex.setProperty(entry.key,entry.value)
    if (keys == null || keys.contains(entry.key))
      index.add(vertex,entry.key,entry.value)
  }
  g.stopTransaction(TransactionalGraph.Conclusion.SUCCESS)
  return vertex
}

def update_indexed_vertex(_id, data, index_name, keys) {
  vertex = g.getRawGraph().getNodeById(_id)
  manager = g.getRawGraph().index()
  index = manager.forNodes(index_name)
  g.setMaxBufferSize(0)
  g.startTransaction()
  index.remove(vertex)
  for (String key in vertex.getPropertyKeys())
    vertex.removeProperty(key)
  for (entry in data.entrySet()) {
    if (entry.value == null) continue;
    vertex.setProperty(entry.key,entry.value)
    if (keys == null || keys.contains(entry.key))
        index.add(vertex,entry.key,entry.value)
  }
  g.stopTransaction(TransactionalGraph.Conclusion.SUCCESS)
  return vertex
}

