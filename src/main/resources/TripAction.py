"""@package TripAction
This module contains all the handlers for /trips/id/action
"""
from flask_restful import Resource
from flask import jsonify, abort, request, make_response
from src.main.com import ResponseMaker, ServerRequest, TokenGenerator
from src.main.com.NotificationManager import NotificationSender
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
		users = MongoController.getCollection("online")
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

		if action["action"] == TripStates.ACTION_PASSENGER_CONFIRM:
			print("Passenger wants to confirm the driver " + trip["_id"])
			return self.confirm_handler(action, trip, user["_id"])

		if action["action"] == TripStates.ACTION_PASSENGER_REJECT:
			print("Passenger wants to reject the driver " + trip["_id"])
			return self.reject_handler(action, trip, user["_id"])

		if action["action"] == TripStates.ACTION_START:
			print("Passenger wants to confirm the driver " + trip["_id"])
			return self.start_handler(action, trip, user["_id"])

		return ResponseMaker.response_object(constants.SUCCESS, ["message", "action"], ["No action performed. Invalid action.", action["action"]])



	def cancel_handler(self, action, trip, userId):
		if not userId == trip["passengerId"] and not userId == trip["driverId"]:
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden - you are not the owner of this trip")
		
		active_trips = MongoController.getCollection("active_trips")
		active_trips.remove( { "_id" : trip["_id"] })
		users = MongoController.getCollection("online")

		users.update( { "_id" : trip["passengerId"] }, { "$set" : { "state" : User.USER_PSG_IDLE, "tripId" : "" } }) 

		if userId != trip["passengerId"]:
			passenger = list(users.find({ "_id" : trip["passengerId"]}))[0]
			NotificationSender().notifyUser(passenger["username"], "Your trip has been canceled!")

		# If trip had a driver, change it's state 
		if trip["driverId"] >= 0:
			users.update( { "_id" : trip["driverId"] }, { "$set" : { "state" : User.USER_DRV_IDLE, "tripId" : "" } }) 
			# Send firebase notification
			driver = list(users.find({ "_id" : trip["driverId"]}))[0]
			NotificationSender().notifyUser(driver["username"], "Your trip has been canceled!")

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
		
		# The user is a passenger
		if not user["state"] == User.USER_DRV_IDLE:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - driver is busy")


		### The action itself:
		#	1) Update the trip to TRIP_ACCEPTED
		#		1bis) Update trip driver info to userId
		#	2) Update driver status to USER_DRV_WAITING_CONFIRMATION
		#	3) Update passenger status to USER_PSG_SELECTING_DRIVER
		#	4) Send firebase notification to passenger

		active_trips = MongoController.getCollection("active_trips")
		active_trips.update( { "_id" : trip["_id"] }, { "$set" : { "state" : TripStates.TRIP_ACCEPTED } })
		active_trips.update( { "_id" : trip["_id"] }, { "$set" : { "driverId" : userId } })
		users.update( { "_id" : userId }, { "$set" : { "state" : User.USER_DRV_WAITING_CONFIRMATION, "tripId" : trip["_id"] } } ) 
		users.update( { "_id" : trip["passengerId"] }, { "$set" : { "state" : User.USER_PSG_SELECTING_DRIVER } } ) 

		trip = list(active_trips.find( { "_id" : trip["_id"] }))[0]

		passenger = list(users.find({ "_id" : trip["passengerId"]}))[0]
		NotificationSender().notifyUser(passenger["username"], "Trip accepted")

		return ResponseMaker.response_object(constants.SUCCESS, ["message", "action", "trip"], ["Trip was accepted. Driver updated.", action["action"], trip])




	def confirm_handler(self, action, trip, userId):
		if not userId == trip["passengerId"]:
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden - you are not the passenger of this trip")
		
		users = MongoController.getCollection("online")
		passenger = list(users.find({"_id" : userId}))
		if len(passenger) > 1:
			return ResponseMaker.response_error(constants.ERROR, "Internal server error - more than one user with same ID.")
		if len(passenger) == 0:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - user not found")
		passenger = passenger[0]

		if not trip["state"] == TripStates.TRIP_ACCEPTED:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - wrong trip state")
		if not passenger["state"] == User.USER_PSG_SELECTING_DRIVER:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - wrong passenger state")

		active_trips = MongoController.getCollection("active_trips")
		active_trips.update( { "_id" : trip["_id"] }, { "$set" : { "state" : TripStates.TRIP_CONFIRMED } } )
		users.update( { "_id" : userId }, { "$set" : { "state" : User.USER_PSG_WAITING_DRIVER } }) 
		users.update( { "_id" : trip["driverId"] }, { "$set" : { "state" : User.USER_DRV_GOING_TO_PICKUP } }) 

		driver = list(users.find({ "_id" : trip["driverId"]}))[0]
		NotificationSender().notifyUser(driver["username"], "Trip confirmed")

		return ResponseMaker.response_object(constants.SUCCESS, ["message", "action", "trip"], ["Trip was updated.", action["action"], trip])



	def reject_handler(self, action, trip, userId):
		if not userId == trip["passengerId"]:
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden - you are not the passenger of this trip")
		
		users = MongoController.getCollection("online")
		passenger = list(users.find({"_id" : userId}))
		if len(passenger) > 1:
			return ResponseMaker.response_error(constants.ERROR, "Internal server error - more than one user with same ID.")
		if len(passenger) == 0:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - user not found")
		passenger = passenger[0]

		if not trip["state"] == TripStates.TRIP_ACCEPTED:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - wrong trip state")
		if not passenger["state"] == User.USER_PSG_SELECTING_DRIVER:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - wrong passenger state")

		active_trips = MongoController.getCollection("active_trips")
		active_trips.update( { "_id" : trip["_id"] }, { "$set" : { "state" : TripStates.TRIP_PROPOSED } } )
		active_trips.update( { "_id" : trip["_id"] }, { "$set" : { "driverId" : -1 } })
		users.update( { "_id" : userId }, { "$set" : { "state" : User.USER_PSG_WAITING_ACCEPT } } ) 
		users.update( { "_id" : trip["driverId"] }, { "$set" : { "state" : User.USER_DRV_IDLE } } ) 

		driver = list(users.find({ "_id" : trip["driverId"]}))[0]
		NotificationSender().notifyUser(driver["username"], "Trip rejected")

		return ResponseMaker.response_object(constants.SUCCESS, ["message", "action", "trip"], ["Trip was updated.", action["action"], trip])

	def start_handler_any(self, action, trip, user):
		users = MongoController.getCollection("online")
		active_trips = MongoController.getCollection("active_trips")

		if user["type"] == User.USER_TYPE_PASSENGER:
			if user["state"] != User.USER_PSG_WAITING_DRIVER:
				return ResponseMaker.response_error(constants.PARAMERR, "Bad request - passenger is not waiting for driver")
			trip_state = TripStates.TRIP_STARTED_PASSENGER
			user_state = User.USER_PSG_WAITING_START


		if user["type"] == User.USER_TYPE_DRIVER:
			if user["state"] != User.USER_DRV_GOING_TO_PICKUP:
				return ResponseMaker.response_error(constants.PARAMERR, "Bad request - driver is not going to pickup")
			trip_state = TripStates.TRIP_STARTED_DRIVER
			user_state = User.USER_DRV_WAITING_START

		active_trips.update( { "_id" : trip["_id"] }, { "$set" : { "state" : trip_state } } )
		users.update( { "_id" : user["_id"] }, { "$set" : { "state" : user_state } } ) 
		return ResponseMaker.response_object(constants.SUCCESS, ["message", "action", "trip"], ["Trip was updated.", action["action"], trip])

		

	def start_handler_passenger(self, action, trip, user):
		users = MongoController.getCollection("online")
		active_trips = MongoController.getCollection("active_trips")
		if user["state"] != User.USER_PSG_WAITING_DRIVER:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - passenger is not waiting for driver")

		driver = list(users.find({ "_id" : trip["driverId"]}))[0]
		if driver["state"] != User.USER_DRV_WAITING_START:
			return ResponseMaker.response_error(constants.ERROR, "Internal server error - driver in a bad state")

		active_trips.update( { "_id" : trip["_id"] }, { "$set" : { "state" : TripStates.TRIP_STARTED } } )
		users.update( { "_id" : user["_id"] }, { "$set" : { "state" : User.USER_PSG_TRAVELING} } ) 
		users.update( { "_id" : driver["_id"] }, { "$set" : { "state" : User.USER_DRV_TRAVELING} } ) 
		return ResponseMaker.response_object(constants.SUCCESS, ["message", "action", "trip"], ["Trip just started.", action["action"], trip])


	def start_handler_driver(self, action, trip, user):
		users = MongoController.getCollection("online")
		active_trips = MongoController.getCollection("active_trips")
		if user["state"] != User.USER_DRV_GOING_TO_PICKUP:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - driver is not going to pickup")

		passenger = list(users.find({ "_id" : trip["passengerId"]}))[0]
		if passenger["state"] != User.USER_PSG_WAITING_START:
			return ResponseMaker.response_error(constants.ERROR, "Internal server error - passenger in a bad state")

		active_trips.update( { "_id" : trip["_id"] }, { "$set" : { "state" : TripStates.TRIP_STARTED } } )
		users.update( { "_id" : user["_id"]}, { "$set" : { "state" : User.USER_DRV_TRAVELING} } ) 
		users.update( { "_id" : passenger["_id"] }, { "$set" : { "state" : User.USER_PSG_TRAVELING} } ) 
		return ResponseMaker.response_object(constants.SUCCESS, ["message", "action", "trip"], ["Trip just started.", action["action"], trip])

	def start_handler(self, action, trip, userId):
		if not userId == trip["passengerId"] and not userId == trip["driverId"]:
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden - you are not the owner of this trip")
	
		if trip["state"] not in TripStates.TRIP_START_VALID:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - this trip cannot start")

		# Retrieve user
		users = MongoController.getCollection("online")
		user = list(users.find({"_id" : userId}))
		if len(user) > 1:
			return ResponseMaker.response_error(constants.ERROR, "Internal server error - more than one user with same ID.")
		if len(user) == 0:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - user not found")
		user = user [0]

		# Anyone can accept first
		if trip["state"] == TripStates.TRIP_CONFIRMED:
			return self.start_handler_any(action, trip, user)
		elif trip["state"] == TripStates.TRIP_STARTED_DRIVER:
			return self.start_handler_passenger(action, trip, user)
		elif trip["state"] == TripStates.TRIP_STARTED_PASSENGER:
			return self.start_handler_driver(action, trip, user)

		return ResponseMaker.response_error(constants.PARAMERR, "Internal server error.")
