"""@package SimpleAPI
Documentation for this module.
More details.
"""

from flask_restful import Resource
from flask import jsonify, abort, request, make_response

import os
import requests
import logging as logger
from src.main.mongodb import MongoController
from src.main.com import ResponseMaker, ServerRequest, TokenGenerator
from config import constants

def validateToken(response):
	if not "UserToken" in request.headers:
		return False
	token = request.headers['UserToken']
	return TokenGenerator.validateToken(token)
	

class Hello(Resource):
	"""This class initializes a resource named Hello.
	It can be called through GET.
	"""
	def get(self):
		print("GET at /")
		logger.getLogger().debug("Hello Logger")
		return 'Hello' 

class GoodBye(Resource):
	"""This class initializes a resource named Goodbye.
	It can be called through GET and POST.
	"""
	def get(self):
		print("GET at /goodbye")
		logger.getLogger().debug("Good Bye Logger")
		return 'Good Bye'

	def post(self):
		print("POST at /goodbye")
		return {'good':'bye'}

class UserById(Resource):
	"""This class initializes a resource named UserById which allows
	the user to perform operations Consult(GET), Update(PUT) and Removal(DELETE)
	through	the user id.
	"""		
	def __init__(self):
		self.users = MongoController.getCollection("users")

	def get(self, id):
		if not validateToken(request):
			return ResponseMaker.response(constants.FORBIDDEN, "Forbidden")

		print("GET at /greet/id")
		candidates = [user for user in self.users.find() if user['_id'] == id]
		if len(candidates) == 0:
			#If not available in local data-base, ask Shared-Server for user info.
			candidates = [ ServerRequest.getUser(id) ]
			self.users.insert_one(candidates[0])
		if len(candidates) == 0:			
			logger.getLogger().error("Attempted to retrieve user with non-existent id.")
			return ResponseMaker.response(constants.NOT_FOUND, "User id not found:" + str(e))
		return jsonify({'greetings': candidates[0]})

	def put(self, id):
		if not validateToken(request):
			return ResponseMaker.response(constants.FORBIDDEN, "Forbidden")
		try:
			#Ask Shared-Server to update this user
			success, updated_user = ServerRequest.updateUser(request.json)		
			if success:
				#Update in local data-base
				self.users.update({updated_user['_id']}, updated_user)
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
		if not validateToken(request):
			return ResponseMaker.response(constants.FORBIDDEN, "Forbidden")

		print(id)
		print("DELETE at /greet/id")

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
		return jsonify({'user': candidates[0]})


class GreetAdd(Resource):
	"""This class initializes a resource named GreetAdd.
	It can be called through GET and POST.
	"""
	def __init__(self):
		self.users = MongoController.getCollection("users")

	def get(self):
		if not validateToken(request):
			return ResponseMaker.response(constants.FORBIDDEN, "Forbidden")
		print("GET at /greet")
		logger.getLogger().info("GET at /greet")
		aux = [user for user in self.users.find()]
		return jsonify({'users' : aux})

	def post(self):
		if not validateToken(request):
			return ResponseMaker.response(constants.FORBIDDEN, "Forbidden")
		print(request.json)
		if (not request.json or not 'user' in request.json):
			logger.getLogger().error("Missing user data to create user.")
			abort(constants.PARAMERR, 'request missing user tag')
		if (not 'id' in  request.json['user']):
			logger.getLogger().error("Attempted to create user without id.")
			abort(constants.PARAMERR, 'request missing id')
		if (not 'name' in request.json['user']):
			logger.getLogger().error("Attempted to create user without name.")
			abort(constants.PARAMERR, 'request missing name')

		id = request.json['user']['id']

		for user in self.users.find():
			if user['_id'] == id:
				logger.getLogger().error("Attempted to create user with existing id.")
				abort(constants.PARAMERR, 'user id already exists')

		name = request.json['user']['name']
		newUser = { '_id' : id, 'name' : name }

		self.users.insert_one(newUser)
		print("POST at /greet")
		return make_response(jsonify({'user' : newUser}), constants.CREATE_SUCCESS)

