
from pymongo import MongoClient
import os
import logging as logger

class MongoHandler(object):
	def __init__(self):
		if 'MONGODB_URL' in os.environ:
			self.db_client = MongoClient(os.environ['MONGODB_URL'])
			logger.getLogger().debug("MONGODB_URL found! Using remote database")
		else:
			self.db_client = MongoClient("mongodb://127.0.0.1:27017/test")
			logger.getLogger().debug("Using local database")
		self.db = self.db_client.get_default_database()
	
	def getCollection(self, collectionName):
		return self.db[collectionName]
