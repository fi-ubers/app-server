from pymongo import MongoClient
import os
import logging as logger

MONGO_DEFAULT_URL = "mongodb://127.0.0.1:27017/test"

"""
Try to load mongo database, check if URL for remote
db is set, otherwise use default localhost
"""

if 'MONGODB_URL' in os.environ:
	db_client = MongoClient(os.environ['MONGODB_URL'])
	logger.getLogger().debug("MONGODB_URL found! Using remote database")
else:
	db_client = MongoClient(MONGO_DEFAULT_URL)
	logger.getLogger().debug("Using local database")
db = db_client.get_default_database()

def getCollection(collectionName):
	return db[collectionName]


"""
.find() --- returns [{object}]
.delete_many(condition)
.insert_one(object)


"""

