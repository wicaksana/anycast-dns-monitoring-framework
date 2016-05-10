import unittest
import anycast_dns_monitoring.data_processing.params as params
from anycast_dns_monitoring.data_processing.db import Db


class DbTest(unittest.TestCase):
    def setUp(self):
        self.db = Db()

    def test_find_one(self):
        query = {'asn': '56203'}
        result = self.db.find_one(col=params.map4, query=query)
        self.assertEqual(len(result), 3)
        self.assertIsNotNone(result)

    def test_find(self):
        query = {'asn': '56203'}
        results = self.db.find(col=params.map4, query=query)
        self.assertIsNotNone(results)

