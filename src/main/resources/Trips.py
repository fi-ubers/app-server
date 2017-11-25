"""@package Trips
This module contains all the handlers for /users/<int:id>/trips, /trips, /trips/estimate and /trips/<int:id> endpoints.
Should allow the user to consult all existing trips, create new ones and validate users with validation of credentials.
"""

from flask_restful import Resource
from flask import jsonify, abort, request, make_response
from src.main.com import ResponseMaker, ServerRequest, TokenGenerator
from src.main.model import User, TripStates

from src.main.mongodb import MongoController
import config.constants as constants

import os
import requests
import uuid
import logging as logger

class Trips(Resource):

	### TODO: move these to another place???
	""" Helper function to check if user is online and a passenger """
	def userId_is_passenger(self, id):
		users_online = MongoController.getCollection("online")

		for user in users_online.find():
			if user["_id"] == id:
				found = user
				return (user, user["type"] == "passenger")
		return (None, False)

	""" Check the validity of a new-trip request """
	def check_new_trip(self, trip):
		required_single = ["origin", "destination", "distance", "duration", "path"]
		required_waypoints = ["coords", "distance", "duration"]
		for field in required_single:
			if not field in trip:
				return False

		for waypoint in trip["path"]:
			for field in required_waypoints:
				if not field in waypoint:
					return False
		return True

	"""
	Computes the euclidian distance between two coordinates
	This is not accurate actually, because coordinates are in
	latitude/logitude.
	"""
	def distance(self, a, b):
		x1 = a["lat"]
		x2 = b["lat"]
		y1 = a["lng"]
		y2 = b["lng"]
		return ( (x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2) )

	"""
	Use POST at /trips to create a new proposed trip as a passenger. It will fail if user is a driver.
	"""
	def post(self):
		print(request.json)
		logger.getLogger().debug("POST at /trips")
		logger.getLogger().debug(request.json)

		# (validate-token) Validate user token
		if not "UserToken" in request.headers:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing token")

		token = request.headers['UserToken']
		(valid, requester) = TokenGenerator.validateToken(token)
		if not valid:
			return ResponseMaker.response_error(constants.UNAUTHORIZED, "Unauthorized")

		# Check if user is 1) logged in, and 2) a passenger
		(user, is_passenger) = self.userId_is_passenger(requester["_id"])

		if user == None:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - user is not logged in")
		if not is_passenger:
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden - user is not passenger")

		logger.getLogger().debug("The 'passenger' requesting the trip is: " + str(user["_id"]) + "-" + user["username"])

		if not user["state"] == User.USER_IDLE:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - user is not in idle state!")

		# Check the trip data is valid!
		trip = request.json
		if trip == None:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing trip data")
		if not self.check_new_trip(trip):
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - bad trip data")

		# Creating a new trip
		new_trip = {}
		new_trip["directions"] = trip
		new_trip["passengerId"] = requester["_id"]
		new_trip["driverId"] = -1
		new_trip["state"] = TripStates.TRIP_PROPOSED
		new_trip["_id"] = str(uuid.uuid1())
		logger.getLogger().debug("Created trip with uudi: " + new_trip["_id"])

		# (mongodb) Storing new trip in the db!
		active_trips = MongoController.getCollection("active_trips")
		active_trips.insert_one(new_trip)
		
		users = MongoController.getCollection("online")
		users.update_one( { "_id" : user["_id"] }, { "$set" : { "state" : User.USER_PSG_WAITING_ACCEPT, "tripId" : new_trip["_id"] } } )

		return ResponseMaker.response_object(constants.SUCCESS, ["message", "trip"], ["Trip created!", new_trip])


	"""
	Get a list of all active trips.
	Requires an UserToken to use. Will fail with 401 if token does not decode.
	Requires user to be a "driver". Will fail with 403 if user is "passanger"
	Allows three in-query parameters 
	"""
	def get(self):
		logger.getLogger().debug("GET at /trips")

		# (validate-token) Validate user token
		if not "UserToken" in request.headers:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing token")

		token = request.headers['UserToken']
		(valid, requester) = TokenGenerator.validateToken(token)
		if not valid:
			return ResponseMaker.response_error(constants.UNAUTHORIZED, "Unauthorized")

		# Check if user is 1) logged in, and 2) a passenger
		(user, is_passenger) = self.userId_is_passenger(requester["_id"])

		if user == None:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - user is not logged in")
		if is_passenger:
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden - user is not driver")

		logger.getLogger().debug("The 'driver' requesting trips is: " + str(user["_id"]) + "-" + user["username"])


		## Actual getting of the trips!
		params = request.args

		active_trips = MongoController.getCollection("active_trips")
		trips = list(active_trips.find())

		if "filter" in params:
			trips = [trip for trip in trips if trip["state"] == params["filter"]]

		if "sort" in params:
			pass

		if "limit" in params:
			limit = int(params["limit"])
			if limit > 0:
				trips = trips[:(limit)]

		return ResponseMaker.response_object(constants.SUCCESS, ["message", "trips"], ["Getting trips!", trips])

class TripsById(Resource):
	"""
	Get a trip by ID
	"""
	def get(self, id):
		logger.getLogger().debug("GET at /trips/" + str(id))

		# (validate-token) Validate user token
		if not "UserToken" in request.headers:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing token")

		token = request.headers['UserToken']
		(valid, response) = TokenGenerator.validateToken(token)

		if not valid:
			return ResponseMaker.response_error(constants.UNAUTHORIZED, "Unauthorized")
		
		active_trips = MongoController.getCollection("active_trips")
		trip = list(active_trips.find({"_id" : id}))

		if len(trip) == 0:
			return ResponseMaker.response_error(constants.NOT_FOUND, "Not found")

		# This should never happen
		if len(trip) > 1:
			return ResponseMaker.response_error(constants.ERROR, "Internal server error - more than one trip with same ID")

		trip = trip[0]
		print(trip)

		return ResponseMaker.response_object(constants.SUCCESS, ["message", "trip"], ["OK", trip])



 #####
 ##### EVERITHING BELOW HERE NEEDS REVISION
 #####

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
			return ResponseMaker.response_error(constants.UNAUTHORIZED, "Unauthorized")

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
		print(request.json)
		logger.getLogger().debug("POST at /trips/estimation")
		logger.getLogger().debug(request.json)

		try:
			# (validate-token) Validate user token
			if not "UserToken" in request.headers:
				return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing token")

			token = request.headers['UserToken']

			(valid, response) = TokenGenerator.validateToken(token)
			if not valid:
				return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden")
			
			#Send trip estimation request to shared server.
			(status, response) = ServerRequest.estimateTrip(request.json)

			if (status != constants.SUCCESS):
				return ResponseMaker.response_error(status, response["message"])
			
			return ResponseMaker.response_object(status, ["cost"], [response])
		except Exception as e:
			logger.getLogger().error("Error " + str(e))
			return ResponseMaker.response_error(constants.ERROR, "Unexpected error" + str(e))
