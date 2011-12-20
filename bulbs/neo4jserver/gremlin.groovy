// Watch out for using Blueprints methods that have internal transactions.
// You'll get better write performance with only using one transaction.
// In other words, don't use:
//  ElementHelper.removeProperties() and ElementHelper.setProperties()
// Don't use Gremlin methods for writes because all contain transactions.
// Actually, Neo4j doesn't support nested transactions -- it ignores
// internal transactions
// http://wiki.neo4j.org/content/Transactions
// http://wiki.neo4j.org/content/Flat_nested_transactions


//
// Index Controller Methods
//


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

//
// Index Container Methods
//
  
// NOTE: Converting all index values to strings because that's what Neo4j does
// anyway, and when using the JSON type system, Rexster doesn't have a way to 
// specify types in the URL for index lookups. This keeps the code consistent.
def create_indexed_vertex(data,index_name,keys) {
  neo4j = g.getRawGraph()
  manager = neo4j.index()
  index = manager.forNodes(index_name)
  //g.setMaxBufferSize(0)
  //g.startTransaction()
  tx = neo4j.beginTx()
  vertex = neo4j.createNode()
  for (entry in data.entrySet()) {
    if (entry.value == null) continue;
    vertex.setProperty(entry.key,entry.value)
    if (keys == null || keys.contains(entry.key))
      index.add(vertex,entry.key,String.valueOf(entry.value))
  }
  //g.stopTransaction(TransactionalGraph.Conclusion.SUCCESS)
  tx.success()
  tx.finish()
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
      index.add(vertex,entry.key,String.valueOf(entry.value))
  }
  g.stopTransaction(TransactionalGraph.Conclusion.SUCCESS)
  return vertex 
}

