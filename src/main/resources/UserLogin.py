"""@package UserLogin
This module contains all the handlers for /users endpoint
Should allow creation and login of users with validation of credentials..
"""

from flask_restful import Resource
from flask import jsonify, abort, request, make_response
from src.main.com import ResponseMaker, ServerRequest 

from src.main.mongodb import MongoController

import os
import logging as logger

class UserLogin(Resource):
	"""This is the handler for user login and credential validation.
	Expects credentials in the body of the request, with UserCredentials format:
		{   "username" : string,
			"password" : string,
			"fbAuthToken" : string
		}
	At least one of password or fbAuthToken.

	Returns a authentication token on success
	"""
	def post(self):
		print(request.json)
		logger.getLogger().debug("POST at /users/login")
		logger.getLogger().debug(request.json)

		# (shared-server) First ask shared server for credentials validation
		server_response = ServerRequest.validateUser(request.json)
		if not server_response:
			return ResponseMaker.response(418, 'I\' m a teapot and your credentials are not valid!')

		print(server_response)
		logger.getLogger().debug("Credentials are valid, server responsed with user")

		# (token-generation) Generate a new UserToken for that user
		token = "AAAABBBBCCCC"
		server_response["token"] = token

		# (mongodb) If credentials are valid, add user to active users table
		"""
		users_online = MongoController.getCollection("online")
		for user in users_online.find():
			if user["_id"] == server_response["_id"]:
				users_online.delete_many({"_id" : user["_id"]}) 
		users_online.insert_one(server_response)
		"""
		return ResponseMaker.response(200, token)
