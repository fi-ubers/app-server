"""@package Paymethods
This module contains all the handlers for /payment endpoint.
Should allow the user to consult all available paymethods.
"""

from flask_restful import Resource
from flask import jsonify, abort, request, make_response
from src.main.com import ResponseMaker, ServerRequest, TokenGenerator

from src.main.mongodb import MongoController
import config.constants as constants

import os
import requests
import logging as logger

class Paymethods(Resource):

	""" Handler to get a list of all users.
	Requieres: user token in the header.
		UserToken : string
	Returns a list of:
	    {
	      "name": "paymethods",
	      "parameters": {}
	    }
	"""
	def get(self):
		logger.getLogger().debug("GET at /payment")
		# (validate-token) Validate user token
		if not "UserToken" in request.headers:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing token")

		token = request.headers['UserToken']

		(valid, response) = TokenGenerator.validateToken(token)

		if not valid:
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden")
		
		status_code, response = ServerRequest.getPaymethods()
		
		if (status_code != constants.SUCCESS):
			return ResponseMaker.response_object(constants.ERROR, response['message'])
			
		print(response)
		
		return ResponseMaker.response_object(constants.SUCCESS, ['paymethods'], [response['paymethods']])




