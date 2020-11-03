import pymongo
from bson import binary
from . import constants

class Database(object):
    URI = constants.MONGO_URI
    DATABASE = None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Database.URI)
        Database.DATABASE = client[constants.DATABASE]

    @staticmethod
    def insert(collection, data):
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def find(collection, query):
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)

    @staticmethod
    def update(collection, old_values, new_values):
        return Database.DATABASE[collection].update_one(old_values, new_values)

    @staticmethod
    def delete(collection, query):
        Database.DATABASE[collection].delete_one(query)

    @staticmethod
    def deletemany(collection, query):
        Database.DATABASE[collection].delete_one(query)
