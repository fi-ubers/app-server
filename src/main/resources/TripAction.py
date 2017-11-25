"""@package TripAction
This module contains all the handlers for /trips/id/action
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


class TripActions(Resource):
	"""
	Perform actions and change trip state
	"""
	def post(self, id):
		logger.getLogger().debug("GET at /trips/" + str(id))

		# (validate-token) Validate user token
		if not "UserToken" in request.headers:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing token")

		token = request.headers['UserToken']
		(valid, user) = TokenGenerator.validateToken(token)

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

		action = request.json
		if action == None:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing action")

		if not "action" in action:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing action")

		if action["action"] == TripStates.ACTION_CANCEL:
			print("Someone wants to delete trip " + trip["_id"])
			return self.cancel_handler(action, trip, user["_id"])

		if action["action"] == TripStates.ACTION_DRIVER_ACCEPT:
			print("Someone wants to accept the trip " + trip["_id"])
			return self.accept_handler(action, trip, user["_id"])

		return ResponseMaker.response_object(constants.SUCCESS, ["message", "action"], ["No action performed. Invalid action.", action["action"]])





	def cancel_handler(self, action, trip, userId):
		if not userId == trip["passengerId"]:
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden - you are not the owner of this trip")
		
		active_trips = MongoController.getCollection("active_trips")
		active_trips.remove( { "_id" : trip["_id"] })
		users = MongoController.getCollection("online")
		users.update( { "_id" : userId }, { "$set" : { "state" : User.USER_IDLE } }) 

		# If trip had a driver, change it's state 
		if trip["driverId"] >= 0:
			users.update( { "_id" : trip["driverId"] }, { "$set" : { "state" : User.USER_IDLE } }) 
			### TODO: send firebase notification

		return ResponseMaker.response_object(constants.SUCCESS, ["message", "action", "trip"], ["Trip was deleted. Passenger updated.", action["action"], trip])




	def accept_handler(self, action, trip, userId):
		if not trip["state"] == TripStates.TRIP_PROPOSED:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - trip is not in valid state to accept.")

		users = MongoController.getCollection("online")
		user = list(users.find({"_id" : userId}))
		if len(user) > 1:
			return ResponseMaker.response_error(constants.ERROR, "Internal server error - more than one user with same ID.")
		if len(user) == 0:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - user not found")

		user = user[0]
		if not user["type"] == User.USER_TYPE_DRIVER:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - user is not driver")
		
		if not user["state"] == User.USER_IDLE:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - driver is busy")


		### The action itself:
		#	1) Update the trip to TRIP_ACCEPTED
		#		1bis) Update trip driver info to userId
		#	2) Update driver status to USER_WAITING_CONFIRMATION
		#	3) Send firebase notification to passenger

		active_trips = MongoController.getCollection("active_trips")
		active_trips.update( { "_id" : trip["_id"] }, { "$set" : { "state" : TripStates.TRIP_ACCEPTED } })
		active_trips.update( { "_id" : trip["_id"] }, { "$set" : { "driverId" : userId } })
		users.update( { "_id" : userId }, { "$set" : { "state" : User.USER_WAITING_CONFIRMATION} }) 

		trip = list(active_trips.find( { "_id" : trip["_id"] }))[0]

		### TODO: send firebase notification to passenger
		return ResponseMaker.response_object(constants.SUCCESS, ["message", "action", "trip"], ["Trip was accepted. Driver updated.", action["action"], trip])

