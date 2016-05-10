from pymongo import MongoClient
import anycast_dns_monitoring.data_processing.params as params


class Db:
    """
    mongodb wrapper
    """
    def __init__(self):
        client = MongoClient()
        self.db = client[params.db]

    def find_one(self, col, query=None):
        return self.db[col].find_one(query)

    def find(self, col, query=None):
        return self.db[col].find(query)

    def drop_collection(self, col):
        self.db[col].drop()

    def insert_many(self, col, data):
        self.db[col].insert_many(data)