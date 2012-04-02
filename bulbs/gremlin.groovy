// 
// Copyright 2012 James Thornton (http://jamesthornton.com)
// BSD License (see LICENSE for details)
//
// Gremlin scripts in Gremlin-Groovy v1.3
//
// See the Gremlin and Blueprints docs for the full Gremlin/Blueprints API. 
//
// Gremlin Wiki:     https://github.com/tinkerpop/gremlin/wiki
// Gremlin Steps:    https://github.com/tinkerpop/gremlin/wiki/Gremlin-Steps
// Gremlin Methods:  https://github.com/tinkerpop/gremlin/wiki/Gremlin-Methods 
// Blueprints Wiki:  https://github.com/tinkerpop/blueprints/wiki
//
// Client-specific methods are defined at the client level.
// e.g. neo4j/gremlin.groovy and rexster/gremlin.groovy
//

// Graph

def get_vertices() { 
  g.getVertices()
}

def get_edges() {
  g.getEdges()
}

// Vertices

// These edge-label conditionals are a messy hack until Gremin allows null labels. 
// See https://github.com/tinkerpop/gremlin/issues/267

// the || label == "null" is a hack until Rexster fixes its null label bug.
// See https://github.com/tinkerpop/rexster/issues/197

def outE(_id, label) {
  if (label == null)
    g.v(_id).outE()
  else
    g.v(_id).outE(label)
}

def inE(_id, label) {
  if (label == null)
    g.v(_id).inE()
  else
    g.v(_id).inE(label)
}

def bothE(_id, label) { 
  if (label == null)
    g.v(_id).bothE()
  else
    g.v(_id).bothE(label)
}

def outV(_id, label) {
  if (label == null)
    g.v(_id).out()
  else
    g.v(_id).out(label)
}

def inV(_id, label) {
  if (label == null)
    g.v(_id).in()
  else
    g.v(_id).in(label)
}

def bothV(_id, label) { 
  if (label == null)
    g.v(_id).both()
  else
    g.v(_id).both(label)
}

// Neo4j requires you delete all adjacent edges first. 
// Blueprints' removeVertex() method does that; the Neo4jServer DELETE URI does not.
def delete_vertex(_id) {
  vertex = g.v(_id)
  g.removeVertex(vertex)
}

// Indices

def index_count(index_name, key, value) {
  index = g.idx(index_name);
  return index.count(key,value);
}

def get_or_create_vertex_index(index_name, index_params) {
  def getOrCreateVertexIndex = { 
    index = g.idx(index_name)
    if (index == null) {
      if (index_params == null) {
        index = g.createManualIndex(index_name, Vertex.class)
      } else {
        index = g.createManualIndex(index_name, Vertex.class, index_params)
      }
    }
    return index
  }
  def transaction = { final Closure closure ->
    g.setMaxBufferSize(0);
    g.startTransaction();
    try {
      results = closure();
      g.stopTransaction(TransactionalGraph.Conclusion.SUCCESS);
      return results; 
    } catch (e) {
      g.stopTransaction(TransactionalGraph.Conclusion.FAILURE);
      throw e;
    }
  }
  return transaction(getOrCreateVertexIndex);
}

def get_or_create_edge_index(index_name, index_params) {
  def getOrCreateEdgeIndex = { 
    index = g.idx(index_name)
    if (index == null) {
      if (index_params == null) {
        index = g.createManualIndex(index_name, Edge.class)
      } else {
        index = g.createManualIndex(index_name, Edge.class, index_params)
      }
    }
    return index
  }
  def transaction = { final Closure closure ->
    g.setMaxBufferSize(0);
    g.startTransaction();
    try {
      results = closure();
      g.stopTransaction(TransactionalGraph.Conclusion.SUCCESS);
      return results; 
    } catch (e) {
      g.stopTransaction(TransactionalGraph.Conclusion.FAILURE);
      throw e;
    }
  }
  return transaction(getOrCreateEdgeIndex);
}

// Utils

def warm_cache() {
  for (vertex in g.getVertices()) {
    vertex.getOutEdges()
  }
}

def load_graphml(uri) {
  g.loadGraphML(uri)
}

def save_graphml() {
  g.saveGraphML('bulbs.graphml')
  new File('bulbs.graphml').getText()
}

def clear() {
  g.clear()
}

//
// Gremln user-defined steps
//
// You must execute the step definition script at least once before you 
// use the steps. For production use, this should really be defined server side.
//

// Tree Steps: inTree() and outTree()
// See https://groups.google.com/d/topic/gremlin-users/iCPUifiU_wk/discussion


// Obsoleted with the addition of the the TreePipe in Gremlin 1.6 
// See https://groups.google.com/d/topic/gremlin-users/9s2YWsqK_Ro/discussion

def define_tree_steps() {
  tree = { vertices ->

    def results = []

    vertices.each() {
      results << it
      children = it."$direction"().toList()
      if (children) {
        child_tree = tree(children)
        results << child_tree
      }
    }
    results
  }

  inClosure = {final Object... params -> 
    try { label = params[0] }
    catch(e){ label = null }
    results = []
    direction = "in"
    _().transform{ tree(it) }
  }    

  outClosure = {final Object... params -> 
    try { label = params[0] }
    catch(e){ label = null }
    results = []
    direction = "out"
    _().transform{ tree(it) }
  }   

  Gremlin.defineStep("inTree", [Vertex,Pipe], inClosure) 
  Gremlin.defineStep("outTree", [Vertex,Pipe], outClosure) 
}
