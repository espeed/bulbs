import unittest
from bulbs.tests import BulbsTestCase, suite
from bulbs.config import Config, REXSTER_URI
from bulbs.rexster import RexsterResource, RexsterIndex

config = Config(REXSTER_URI)
BulbsTestCase.resource = RexsterResource(config)
BulbsTestCase.index_class = RexsterIndex

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
