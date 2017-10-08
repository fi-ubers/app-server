"""@package SimpleAPI
Documentation for this module.
More details.
"""

from flask_restful import Resource
from flask import jsonify, abort, request, make_response

import os
import logging as logger

from src.main.mongodb import MongoController
from src.main.com import ResponseMaker
from src.main.com import ServerRequest

def validateToken(response):
	if not "UserToken" in request.headers:
		return False
	token = request.headers['UserToken']
	print(token)
	return token == "AAAABBBBCCCC"

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

class Greet(Resource):
	"""This class initializes a resource named Greet.
	It can be called through GET and DELETE.
	"""
	def __init__(self):
		self.users = MongoController.getCollection("users")

	def get(self, id):
		if not validateToken(request):
			return ResponseMaker.response(403, "Forbidden")

		print("GET at /greet/id")
		candidates = [user for user in self.users.find() if user['_id'] == id]
		if len(candidates) == 0:
			logger.getLogger().error("Attempted to retrieve user with non-existent id.")
			abort(404, 'user id not found')
		return jsonify({'greetings': candidates[0]})

	def delete(self, id):
		if not validateToken(request):
			return ResponseMaker.response(403, "Forbidden")
		print(id)
		print("DELETE at /greet/id")

		candidates = [user for user in self.users.find() if user['_id'] == id]

		if len(candidates) == 0:
			logger.getLogger().error("Attempted to delete user with non-existent id.")
			abort(404, 'user id not found')
		logger.getLogger().info("Successfully deleted user.")
		self.users.delete_many({"_id" : candidates[0]['_id']})
		return jsonify({'user': candidates[0]})


class GreetAdd(Resource):
	"""This class initializes a resource named GreetAdd.
	It can be called through GET and POST.
	"""
	def __init__(self):
		self.users = MongoController.getCollection("users")

	def get(self):
		if not validateToken(request):
			return ResponseMaker.response(403, "Forbidden")
		print("GET at /greet")
		logger.getLogger().info("GET at /greet")
		aux = [user for user in self.users.find()]
		return jsonify({'users' : aux})

	def post(self):
		if not validateToken(request):
			return ResponseMaker.response(403, "Forbidden")
		print(request.json)
		if (not request.json or not 'user' in request.json):
			logger.getLogger().error("Missing user data to create user.")
			abort(400, 'request missing user tag')
		if (not 'id' in  request.json['user']):
			logger.getLogger().error("Attempted to create user without id.")
			abort(400, 'request missing id')
		if (not 'name' in request.json['user']):
			logger.getLogger().error("Attempted to create user without name.")
			abort(400, 'request missing name')

		id = request.json['user']['id']

		for user in self.users.find():
			if user['_id'] == id:
				logger.getLogger().error("Attempted to create user with existing id.")
				abort(400, 'user id already exists')

		name = request.json['user']['name']
		newUser = { '_id' : id, 'name' : name }

		self.users.insert_one(newUser)
		print("POST at /greet")
		return make_response(jsonify({'user' : newUser}), 201)


class UserGetAll(Resource):
	
	def get(self):
		return ServerRequest.getUsers()

class UserGetById(Resource):
			
	def get(self, id):
		return ServerRequest.getUser(id)	
		
	def put(self, id):
		return ServerRequest.updateUser(request.json)		
	
	def delete(self, id):
		return ServerRequest.deleteUser(id)

