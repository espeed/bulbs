import unittest

from bulbs.rexster.tests.bulbs_tests import rexster_bulbs_suite
from bulbs.rexster.tests.resource_tests import rexster_resource_suite

from bulbs.neo4jserver.tests.bulbs_tests import neo4j_bulbs_suite
from bulbs.neo4jserver.tests.resource_tests import neo4j_resource_suite

def suite():
    # This requires Neo4j Server and Rexster are running.
    
    suite = unittest.TestSuite()

    suite.addTest(rexster_resource_suite())
    suite.addTest(rexster_bulbs_suite())

    suite.addTest(neo4j_resource_suite()) 
    suite.addTest(neo4j_bulbs_suite())
 
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

    



