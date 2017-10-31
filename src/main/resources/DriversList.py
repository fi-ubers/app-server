from flask_restful import Resource
from flask import jsonify, abort, request, make_response
from src.main.com import ResponseMaker, ServerRequest, TokenGenerator

from src.main.mongodb import MongoController
import config.constants as constants

import os
import requests
import logging as logger

class DriversList(Resource):
	"""Allows the user to get information specific to drivers.
	"""
	def __init__(self):
		self.users = MongoController.getCollection("users")

	def get(self):
		if not validateToken(request):
			return ResponseMaker.response(constants.FORBIDDEN, "Forbidden")

		drivers = [user for user in self.users.find() if user['type'] == "driver"] #TODO: check availability
		
		#If not available in local data-base, ask Shared-Server for user info.
		#drivers = [ ServerRequest.getUsers() ] get available drivers from Shared Server asychronously(?
		#bring them and insert them into the local database
		#self.users.insertMany(drivers)
		if len(drivers) == 0:
			return ResponseMaker.response(constants.NOT_FOUND, "There are no available drivers at the moment.")
		return jsonify({'drivers': drivers})

