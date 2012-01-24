class Hackers(neo4j.Traversal):
    types = [
        neo4j.Outgoing.knows,
        neo4j.Outgoing.coded_by,
        ]
    order = neo4j.DEPTH_FIRST
    stop = neo4j.STOP_AT_END_OF_GRAPH

    def isReturnable(self, position):
        return (not position.is_start
                and position.last_relationship.type == 'coded_by')

# Usage:
for hacker_node in Hackers(traversal_start_node):
    # do stuff with hacker_node
