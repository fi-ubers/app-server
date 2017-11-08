"""@package Trips
This module contains all the handlers for /users/<int:id>/trips, /trips, /trips/estimate and /trips/<int:id> endpoints.
Should allow the user to consult all existing trips, create new ones and validate users with validation of credentials.
"""

from flask_restful import Resource
from flask import jsonify, abort, request, make_response
from src.main.com import ResponseMaker, ServerRequest, TokenGenerator

from src.main.mongodb import MongoController
import config.constants as constants

import os
import requests
import logging as logger


class Trips(Resource):

	def post(self):
		print(request.json)
		logger.getLogger().debug("POST at /trips")
		logger.getLogger().debug(request.json)

		try:
			#Create trip at shared server.
			(status, response) = ServerRequest.createTrip(request.json)
			print("RESPONSE: " + str(response))
			if (status != constants.CREATE_SUCCESS):
				print("NO SUCCESS " + str(status))
				return ResponseMaker.response_error(status, response["message"])
			#TODO:Update local database
			trip = response
			return ResponseMaker.response_object(status, ["trip"], [trip])
		except Exception, e:
			print("Error " + str(e))
			return ResponseMaker.response_error(constants.ERROR, "Unexpected error")

class UserTrips(Resource):
	"""Receives a user id. Returns a json structure with a list containing
	all the trips made by that user.
	"""
	def get(self, id):
		logger.getLogger().debug("GET at /users/" + str(id) +"/trips")
		if not "UserToken" in request.headers:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing token")

		token = request.headers['UserToken']

		(valid, decoded) = TokenGenerator.validateToken(token)

		if not valid or (decoded['_id'] != id):
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden")

		print("GET at /user/id/trips")
		#TODO: search local database
		trips = [] #[user for user in self.users.find() if user['_id'] == id]

		if len(trips) == 0:
			#If not available in local data-base, ask Shared-Server for user info.
			(status, response) = ServerRequest.getUserTrips(id)

			if (status != constants.SUCCESS):
				return ResponseMaker.response_error(status, response["message"])

		#TODO: fetch user from ss and store locally
		trips = response

		if (status == constants.NOT_FOUND):
			logger.getLogger().error("Attempted to retrieve non-existent user trip list.")
			return ResponseMaker.response_error(constants.NOT_FOUND, "Trip list not found.")

		return ResponseMaker.response_object(constants.SUCCESS, ['trips'], [trips])


class TripEstimation(Resource):

	def post(self):
		raise NotImplemented


class TripsById(Resource):

	def get(self):
		raise NotImplemented
