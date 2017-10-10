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

		# (shared-server) First ask shared server for credentials validation
		server_response = ServerRequest.validateUser(request.json)

		if not server_response[0]:
			return ResponseMaker.response(418, 'I\' m a teapot and your credentials are not valid!')
		print("USER VALIDATED: " + str(server_response[1]))
		logger.getLogger().debug("Credentials are valid, server responsed with user")

		user_js = server_response[1];

		# (token-generation) Generate a new UserToken for that user
		token = TokenGenerator.generateToken(server_response[1]);
		user_js["token"] = token

		# (mongodb) If credentials are valid, add user to active users table
		
		users_online = MongoController.getCollection("online")
		for user in users_online.find():
			if user["_id"] == server_response[1]["_id"]:
				users_online.delete_many({"_id" : user["_id"]}) 
		users_online.insert_one(server_response[1])
		
		return ResponseMaker.response(200, { "user" : server_response ,"token" : token })


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
		if not "UserToken" in request.headers:
			return ResponseMaker.response(400, "Bad request - missing token")
		token = request.headers['UserToken']

		result = TokenGenerator.validateToken(token)

		if not result[0]:
			return ResponseMaker.response(403, "Forbidden")

		username = result[1]

		# Token is valid, time to get the users
		print(username)
		logger.getLogger().debug(username)

		# (mongodb) Return all logged in users.
		users_online = MongoController.getCollection("online")

		aux = [user for user in users_online.find()]

		return ResponseMaker.response(501, {'users' : aux})


class UserLogout(Resource):
	def post(self):
		print(request.json)
		logger.getLogger().debug("POST at /users")
		logger.getLogger().debug(request.json)

		if not "UserToken" in request.headers:
			return ResponseMaker.response(400, "Bad request - missing token")
		token = request.headers['UserToken']

		result = TokenGenerator.validateToken(token)

		# (mongodb) Return all logged in users.
		users_online = MongoController.getCollection("online")

		user = [user for user in users_online.find() if (user['username'] == result[1]['username'])]
		print(user)
		if (len(user) == 0):
			return ResponseMaker.response(404, "User not found")

		users_online.delete_many(user[0]);
		
		return ResponseMaker.response(200, { 'users' : user[0] } )


class UserById(Resource):
	"""This class initializes a resource named UserById which allows
	the user to perform operations Consult(GET), Update(PUT) and Removal(DELETE)
	through	the user id.
	"""		
	def __init__(self):
		self.users = MongoController.getCollection("online")

	def get(self, id):
		if not validateToken(request):
			return ResponseMaker.response(constants.FORBIDDEN, "Forbidden")

		print("GET at /user/id")
		candidates = [user for user in self.users.find() if user['_id'] == id]

		if len(candidates) == 0:
			#If not available in local data-base, ask Shared-Server for user info.
			candidates = [ ServerRequest.getUser(id) ]
			self.users.insert_one(candidates[0])

		if len(candidates) == 0:		
			logger.getLogger().error("Attempted to retrieve user with non-existent id.")
			return ResponseMaker.response(constants.NOT_FOUND, "User id not found:" + str(e))

		return jsonify({'users': candidates[0]})


	def put(self, id):

		print(id)
		print("PUT at /user/id")
		(valid, decoded) = validateToken(request)

		if not valid or (decoded['_id'] != id):
			return ResponseMaker.response(constants.FORBIDDEN, "Forbidden")

		try:
			#Ask Shared-Server to update this user
			success, updated_user = ServerRequest.updateUser(request.json)		
			if success:
				#Update in local data-base
				self.users.update({updated_user['_id']}, updated_user) # ???
				logger.getLogger().info("Successfully updated user")
				return ResponseMaker.response(constants.SUCCESS, "User updated successfully!")
			return ResponseMaker.response(constants.NOT_FOUND, "User not found!")	
		except ValueError, e:
			logger.getLogger().error(str(e))
			return ResponseMaker.response(constants.UPDATE_CONFLICT, "User update failed:" + str(e))
		except requests.exceptions.Timeout:	
			logger.getLogger().error(str(e))	
			return ResponseMaker.response(constants.REQ_TIMEOUT, "User update failed:" + str(e))
		except Exception, e:
			logger.getLogger().error(str(e))
			return ResponseMaker.response(constants.FORBIDDEN, "Forbidden")		
		
	def delete(self, id):
		print(id)
		print("DELETE at /greet/id")

		(valid, decoded) = validateToken(request)

		if not valid or (decoded['_id'] != id):
			return ResponseMaker.response(constants.FORBIDDEN, "Forbidden")

		try:
			#Ask Shared-Server to delete this user
			delete_success, status_code = ServerRequest.deleteUser(user['_id'])
			if delete_success:
				#Delete in local data-base
				candidates = [user for user in self.users.find() if user['_id'] == id]
				self.users.delete_many({"_id" : candidates[0]['_id']})
				logger.getLogger().info("Successfully deleted user.")			
			else:
				logger.getLogger().error("Attempted to delete user with non-existent id.")
			return ResponseMaker.response(constants.NOT_FOUND, "User not found!")
		except Exception, e:
			logger.getLogger().error("User delete operation was unsuccessful." + str(e))
			return ResponseMaker.response(status_code, str(e))	
		return make_response(jsonify({'user': candidates[0]}), 200)

