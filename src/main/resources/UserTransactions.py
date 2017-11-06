"""@package UserTransactions
This module contains all the handlers for /users/<int:userId>/transactions endpoint.
Should allow the user to consult all existing transactions or create new ones with validation of credentials.
"""

from flask_restful import Resource
from flask import jsonify, abort, request, make_response
from src.main.com import ResponseMaker, ServerRequest, TokenGenerator

from src.main.mongodb import MongoController
import config.constants as constants

import os
import requests
import logging as logger


class UserTransactions(Resource):
	def __init__(self):
		self.users = MongoController.getCollection("online")

	def get(self, id):
		logger.getLogger().debug("GET at /users/" + str(id) + "/transactions")
		if not "UserToken" in request.headers:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing token")

		token = request.headers['UserToken']

		(valid, decoded) = TokenGenerator.validateToken(token)

		print(decoded)
		if not valid or (decoded['_id'] != id):
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden")
		
		transactions = []#TODO:try fetch transactions from local database

		try:
			if (len(transactions) == 0):
				status_code, transactions = ServerRequest.getUserTransactions(id)
		except Exception, e:
			print(str(e))
			return ResponseMaker.response_error(constants.NOT_FOUND, "User id did not match any existing users." + str(e))			
		return ResponseMaker.response_object(constants.SUCCESS, ['transactions'], [transactions])
	
#	def post(self, id):
#		print(request.json)
#		logger.getLogger().debug("POST at /users/"+str(id)+"/transactions")
#		logger.getLogger().debug(request.json)
		
#		try:

#			if not "UserToken" in request.headers:
#				return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing token")

#			token = request.headers['UserToken']

#			(valid, decoded) = TokenGenerator.validateToken(token)

#			print(decoded)
#			if not valid or (decoded['_id'] != id):
#				return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden")

			#Make Payment.
#			(status, response) = ServerRequest.makePayment(id, request.json)
		
#			if (status != constants.CREATE_SUCCESS):
#				return ResponseMaker.response_error(status, response["message"])
			#TODO:Update local database
#			transaction = response
#			transaction["_id"] = transaction.pop("id")
			#self.users.update({"_id": id}, { $push: { "transactions": transaction } })
#			return ResponseMaker.response_object(status, ["car"], [car])

#		except Exception, e:
#			return ResponseMaker.response_error(constants.ERROR, "Unexpected error")			

