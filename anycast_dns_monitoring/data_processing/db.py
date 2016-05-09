from pymongo import MongoClient
import anycast_dns_monitoring.data_processing.params as params


class Db:
    """
    mongodb helper
    """
    def __init__(self):
        self.db = MongoClient()[params.db]

    def initiate(self):
        return self.db
