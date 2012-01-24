
def hackers(start_node):
    script = "g.v(%s).outE('knows').inV.loop(2).outE('coded_by').inV" % (start_node) 
    return Gremlin().query(script)

# Usage:
for hacker_node in hackers(traversal_start_node):
    # do stuff with hacker_node
