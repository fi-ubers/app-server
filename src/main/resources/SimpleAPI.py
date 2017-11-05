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
		return 'Welcome! App-server is up and running!'

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
	

class GreetAdd(Resource):
	"""This class initializes a resource named GreetAdd.
	It can be called through GET and POST.
	"""
	def __init__(self):
		self.users = MongoController.getCollection("users")

	def get(self):
		if not validateToken(request):
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden")
		print("GET at /greet")
		logger.getLogger().info("GET at /greet")
		aux = [user for user in self.users.find()]
		return jsonify({'users' : aux})

	def post(self):
		if not validateToken(request):
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden")
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

