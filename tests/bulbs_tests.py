import unittest

from bulbs.rexster.tests.bulbs_tests import test_suite as rexster_bulbs_suite
from bulbs.rexster.tests.client_tests import rexster_client_suite

from bulbs.neo4jserver.tests.bulbs_tests import test_suite as neo4j_bulbs_suite
from bulbs.neo4jserver.tests.client_tests import neo4j_client_suite

from bulbs.titan.tests.bulbs_tests import test_suite as titan_bulbs_suite
from bulbs.titan.tests.client_tests import titan_client_suite


def suite():
    # This requires Neo4j Server and Rexster are running.
    
    suite = unittest.TestSuite()

    suite.addTest(rexster_client_suite())
    suite.addTest(rexster_bulbs_suite())

    suite.addTest(neo4j_client_suite()) 
    suite.addTest(neo4j_bulbs_suite())

    suite.addTest(titan_client_suite()) 
    suite.addTest(titan_bulbs_suite())
 
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

    



