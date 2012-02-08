import unittest
from resource_tests import neo4j_resource_suite
from bulbs_tests import test_suite as bulbs_test_suite


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(neo4j_resource_suite())
    suite.addTest(bulbs_test_suite())
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

