"""@package UserLogin
This module contains all the handlers for /users endpoint
Should allow creation and login of users with validation of credentials..
"""

from flask_restful import Resource
from flask import jsonify, abort, request, make_response
from src.main.com import ResponseMaker, ServerRequest, TokenGenerator

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

	Returns a authentication token on success in the form of:
		{ "token" : string }

	Token created in base of user id and a secret app password.
	"""
	def post(self):
		print(request.json)
		logger.getLogger().debug("POST at /users/login")
		logger.getLogger().debug(request.json)

		# (validate-data) Validate user data

		# (shared-server) First ask shared server for credentials validation
		server_response = ServerRequest.validateUser(request.json)

		if not server_response[0]:
			return ResponseMaker.response(418, 'I\' m a teapot and your credentials are not valid!')
		print("USER VALIDATED: " + str(server_response[1]))
		logger.getLogger().debug("Credentials are valid, server responsed with user")

		# (token-generation) Generate a new UserToken for that user
		token = "AAAABBBBCCCC"
		server_response[1]["token"] = token

		# (mongodb) If credentials are valid, add user to active users table
		"""
		users_online = MongoController.getCollection("online")
		for user in users_online.find():
			if user["_id"] == server_response["_id"]:
				users_online.delete_many({"_id" : user["_id"]}) 
		users_online.insert_one(server_response)
		"""
		return ResponseMaker.response(200, token)


class UsersList(Resource):
	"""This is the handler for user creation.
	Params: user data and credentials in the body of the request, with UserCredentials format:
		{   "username" : string,
			"password" : string,
			"type" : string,
			"fb" : {
				"fbId" : string,
				"fbToken" : string
			}
			"firstName" : string,
			"lastName" : string,
			"country" : string,
			"email" : string,
			"birthdate" : string,
			"images" : string,
		}

	Creates a new user based on the data provided.
	Returns:
		201: CREATED (sunny day)
		{	"_id" : integer,
			"ref" : string,
			"username" : string,
			"cars" : array of Cars,
			"firstName" : string,
			"lastName" : string,
			"country" : string,
			"email" : string,
			"birthdate" : string,
			"images" : string
		}
		40X: On user parameter error
		{ "code" : integer, "message" : string }	
		50X: Other type or error (example, no connection with shared or bdd)
	"""
	def post(self):
		print(request.json)
		logger.getLogger().debug("POST at /users")
		logger.getLogger().debug(request.json)

		# (validate-data) Validate user data

		# (shared-server) Send new user data to shared server.
		ServerRequest.createUser(request.json)

		return ResponseMaker.response(501, "Not implemented")

	""" Handler to get a list of all users.
	Requieres: user token in the header.
		UserToken : string
	Returns a list of
		{	"_id" : integer,
			"ref" : string,
			"username" : string,
			"cars" : array of Cars,
			"firstName" : string,
			"lastName" : string,
			"country" : string,
			"email" : string,
			"birthdate" : string,
			"images" : string
		}
	"""
	def get(self):

		# (validate-token) Validate user token
		# (mongodb) Return all logged in users.

		return ResponseMaker.response(501, "Not implemented")

