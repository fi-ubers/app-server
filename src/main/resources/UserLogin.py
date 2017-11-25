"""@package UserLogin
This module contains all the handlers for /users endpoint
Should allow creation and login of users with validation of credentials..
"""

from flask_restful import Resource
from flask import jsonify, abort, request, make_response
from src.main.com import ResponseMaker, ServerRequest, TokenGenerator
from src.main.mongodb import MongoController
from src.main.model import User
import config.constants as constants

import os
import requests
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
		logger.getLogger().debug("POST at /users/login")
		logger.getLogger().debug(request.json)
		try:
			# (shared-server) First ask shared server for credentials validation
			(valid, response) = ServerRequest.validateUser(request.json)
			print "VALIDATION: " + str((valid, response))
		
			if not valid:
				logger.getLogger().debug('Error 418: I\' m a teapot and your credentials are not valid!')
				return ResponseMaker.response_error(response.status_code, "Shared server error")
			logger.getLogger().debug("Credentials are valid, server responsed with user")

			user_js = User.UserJSON(response)

			# (token-generation) Generate a new UserToken for that user
			token = TokenGenerator.generateToken(response);
			# user_js["token"] = token

			users_online = MongoController.getCollection("online")
			# (mongodb) If credentials are valid, add user to active users table
			for user in users_online.find():
				if user_js["_id"] == response["_id"]:
					users_online.delete_many({"_id" : user_js["_id"]})			

			user_js = User.UserJSON(user_js)
			user_js["online"] = True

			users_online.insert_one(user_js)

			return ResponseMaker.response_object(constants.SUCCESS, ['user', 'token'], [user_js, token])
		except Exception as e:
			logger.getLogger().exception(str(e))
			print(str(e))
			return ResponseMaker.response_error(500, "Internal Error")

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
			"firstname" : string,
			"lastname" : string,
			"country" : string,
			"email" : string,
			"birthdate" : string,
			"images" : [string],
		}

	Creates a new user based on the data provided.
	Returns:
		201: CREATED (sunny day)
		{	"_id" : integer,
			"ref" : string,
			"username" : string,
			"cars" : array of Cars,
			"firstname" : string,
			"lastname" : string,
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

		# (shared-server) Send new user data to shared server.
		(status, response) = ServerRequest.createUser(request.json)

		if (status != constants.CREATE_SUCCESS):
			return ResponseMaker.response_error(status, response['message'])
		
		user_js = User.UserJSON(response)
		users_online = MongoController.getCollection("online")
		users_online.insert_one(user_js)

		return ResponseMaker.response_object(status, ['user'], [user_js])

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
		logger.getLogger().debug("GET at /users")
		# (validate-token) Validate user token
		if not "UserToken" in request.headers:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing token")

		token = request.headers['UserToken']

		(valid, response) = TokenGenerator.validateToken(token)

		if not valid:
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden")

		print(response)

		# (mongodb) Return all logged in users.
		users_online = MongoController.getCollection("online")
		aux = [User.UserJSON(user) for user in users_online.find()]

		return ResponseMaker.response_object(constants.SUCCESS, ['users'], [aux])


class UserLogout(Resource):
	def post(self):
		print(request.json)
		logger.getLogger().debug("POST at /users/logout")
		logger.getLogger().debug(request.json)

		if not "UserToken" in request.headers:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing token")
		token = request.headers['UserToken']

		result = TokenGenerator.validateToken(token)

		# (mongodb) Return all logged in users.
		users_online = MongoController.getCollection("online")

		user = [User.UserJSON(user) for user in users_online.find() if (user['username'] == result[1]['username'])]

		if (len(user) == 0):
			return ResponseMaker.response_error(constants.NOT_FOUND, "User not found")

		#users_online.delete_many(user[0]);
		users_online.update({"_id" : user[0]["_id"]}, {"$set":{"online":False}})

		return ResponseMaker.response_object(constants.SUCCESS, ['user'], [user[0]] )


class UserById(Resource):
	"""This class initializes a resource named UserById which allows
	the user to perform operations Consult(GET), Update(PUT) and Removal(DELETE)
	through	the user id.
	"""
	def __init__(self):
		self.users = MongoController.getCollection("online")

	def get(self, id):
		logger.getLogger().debug("GET at /users/" + str(id))
		if not "UserToken" in request.headers:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing token")

		token = request.headers['UserToken']

		(valid, decoded) = TokenGenerator.validateToken(token)

		print("GET at /user/id")
		candidates = [user for user in self.users.find() if user['_id'] == id]

		if len(candidates) == 0:
			#If not available in local data-base, ask Shared-Server for user info.
			(status, response) = ServerRequest.getUser(id)

			if (status != constants.SUCCESS):
				return ResponseMaker.response_error(status, response["message"])

			candidates = [ response ]
			user = candidates[0]
			self.users.insert_one(user)

		if len(candidates) == 0:
			logger.getLogger().error("Attempted to retrieve user with non-existent id.")
			return ResponseMaker.response_error(constants.NOT_FOUND, "User id not found:" + str(e))

		return ResponseMaker.response_object(constants.SUCCESS, ['user'], [User.UserJSON(candidates[0])])


	def put(self, id):
		print(id)
		print("PUT at /user/id")
		logger.getLogger().debug("PUT at /users/" + str(id))

		if not "UserToken" in request.headers:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing token")

		token = request.headers['UserToken']
		(valid, decoded) = TokenGenerator.validateToken(token)

		if not valid or (decoded['_id'] != id):
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden")
		try:
			#Ask Shared-Server to update this user
			success, updated_user = ServerRequest.updateUser(request.json)
			if success:
				#Update in local data-base
				self.users.update({'_id':updated_user['id']}, User.UserJSON(updated_user),  upsert= True)
				logger.getLogger().info("Successfully updated user")
				return ResponseMaker.response_error(constants.SUCCESS, "User updated successfully!")
			return ResponseMaker.response_error(constants.NOT_FOUND, "User not found!")
		except ValueError as e:
			logger.getLogger().error(str(e))
			return ResponseMaker.response_error(constants.UPDATE_CONFLICT, "User update failed:" + str(e))
		except requests.exceptions.Timeout as e:
			logger.getLogger().error(str(e))
			return ResponseMaker.response_error(constants.REQ_TIMEOUT, "User update failed:" + str(e))
		except Exception as e:
			logger.getLogger().error(str(e))
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden: " + str(e))

	def delete(self, id):
		print("DELETE at /users/id")
		logger.getLogger().debug("DELETE at /users/" + str(id))

		if not "UserToken" in request.headers:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing token")

		token = request.headers['UserToken']

		(valid, decoded) = TokenGenerator.validateToken(token)

		print(decoded)
		if not valid or (decoded['_id'] != id):
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden")

		#Ask Shared-Server to delete this user
		delete_success, status_code = ServerRequest.deleteUser(id)
		if delete_success:
			#Delete in local data-base
			candidates = [User.UserJSON(user) for user in self.users.find() if user['_id'] == id]
			self.users.delete_many({"_id" : id })
			logger.getLogger().info("Successfully deleted user.")
		else:
			logger.getLogger().error("Attempted to delete user with non-existent id.")
			return ResponseMaker.response_error(status_code, "Delete error")

		return ResponseMaker.response_object(constants.DELETE_SUCCESS, ['user'], candidates)


