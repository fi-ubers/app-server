"""@package TripAction
This module contains all the handlers for /trips/id/action
"""
from flask_restful import Resource
from flask import jsonify, abort, request, make_response
from src.main.com import ResponseMaker, ServerRequest, TokenGenerator, Distances
from src.main.com.NotificationManager import NotificationSender
from src.main.model import User, TripStates

from src.main.mongodb import MongoController
import config.constants as constants

import os
import requests
import uuid
import logging as logger
import datetime


"""
This is the maximum distance between who users in order to be considered part of the same trip.
"""
MAXIMUM_USER_DISTANCE = 500


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
		#print(trip)

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
			print("Someone wants to start the trip " + trip["_id"])
			return self.start_handler(action, trip, user["_id"])

		if action["action"] == TripStates.ACTION_FINISH:
			print("Someone wants to finish the trip" + trip["_id"])
			return self.finish_handler(action, trip, user["_id"])

		if action["action"] == TripStates.ACTION_RATE:
			print("Passenger wants to rate the driver " + trip["_id"])
			if not "rating" in action:
				return ResponseMaker.response_error(constants.PARAMERR, "Bad request - rating action without rating")
			return self.rate_handler(action, trip, user["_id"])

		if action["action"] == TripStates.ACTION_PAY:
			print("Passenger wants to pay " + trip["_id"])
			if not "paymethod" in action:
				return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing payment info")
			return self.payment_handler(action, trip, user["_id"])

		return ResponseMaker.response_object(constants.SUCCESS, ["message", "action"], ["No action performed. Invalid action.", action["action"]])



	def cancel_handler(self, action, trip, userId):
		if not userId == trip["passengerId"] and not userId == trip["driverId"]:
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden - you are not the owner of this trip")

		if not trip["state"] in TripStates.TRIP_CANCELABLE:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - this trip cannot be cancelled")
		
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

		trip = list(active_trips.find({"_id" : trip["_id"]}))[0]
		print(trip)
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
		NotificationSender().notifyUser(passenger["username"], "Driver confirmed")

		trip = list(active_trips.find({"_id" : trip["_id"]}))[0]
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

		driver = list(users.find({ "_id" : trip["driverId"]}))[0]

		active_trips = MongoController.getCollection("active_trips")
		active_trips.update( { "_id" : trip["_id"] }, { "$set" : { "state" : TripStates.TRIP_PROPOSED } } )
		active_trips.update( { "_id" : trip["_id"] }, { "$set" : { "driverId" : -1 } })
		users.update( { "_id" : userId }, { "$set" : { "state" : User.USER_PSG_WAITING_ACCEPT } } ) 
		users.update( { "_id" : trip["driverId"] }, { "$set" : { "state" : User.USER_DRV_IDLE } } ) 
		users.update( { "_id" : trip["driverId"] }, { "$set" : { "tripId" : "" } } ) 

		NotificationSender().notifyUser(driver["username"], "Trip rejected")
		NotificationSender().notifyUser(passenger["username"], "Driver rejected!")

		trip = list(active_trips.find({"_id" : trip["_id"]}))[0]
		return ResponseMaker.response_object(constants.SUCCESS, ["message", "action", "trip"], ["Trip was updated.", action["action"], trip])

	def start_handler_any(self, action, trip, user):
		users = MongoController.getCollection("online")
		active_trips = MongoController.getCollection("active_trips")
		
		if user["type"] == User.USER_TYPE_PASSENGER:
			if user["state"] != User.USER_PSG_WAITING_DRIVER:
				return ResponseMaker.response_error(constants.PARAMERR, "Bad request - passenger is not waiting for driver")
			trip_state = TripStates.TRIP_STARTED_PASSENGER
			user_state = User.USER_PSG_WAITING_START
			theother = list(users.find({ "_id" : trip["driverId"]}))[0]

		if user["type"] == User.USER_TYPE_DRIVER:
			if user["state"] != User.USER_DRV_GOING_TO_PICKUP:
				return ResponseMaker.response_error(constants.PARAMERR, "Bad request - driver is not going to pickup")
			trip_state = TripStates.TRIP_STARTED_DRIVER
			user_state = User.USER_DRV_WAITING_START
			theother = list(users.find({ "_id" : trip["passengerId"]}))[0]

		active_trips.update( { "_id" : trip["_id"] }, { "$set" : { "time_start_waiting" :  datetime.datetime.now().isoformat() } } )
		active_trips.update( { "_id" : trip["_id"] }, { "$set" : { "state" : trip_state } } )
		users.update( { "_id" : user["_id"] }, { "$set" : { "state" : user_state } } ) 

		# Send notification to the other user 
		NotificationSender().notifyUser(theother["username"], user["username"] + " is ready to start the trip!")

		trip = list(active_trips.find({"_id" : trip["_id"]}))[0]
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
		active_trips.update( { "_id" : trip["_id"] }, { "$set" : { "time_start" :  datetime.datetime.now().isoformat() } } )
		users.update( { "_id" : user["_id"] }, { "$set" : { "state" : User.USER_PSG_TRAVELING} } ) 
		users.update( { "_id" : driver["_id"] }, { "$set" : { "state" : User.USER_DRV_TRAVELING} } ) 

		trip = list(active_trips.find({"_id" : trip["_id"]}))[0]
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
		active_trips.update( { "_id" : trip["_id"] }, { "$set" : { "time_start" :  datetime.datetime.now().isoformat() } } )
		users.update( { "_id" : user["_id"]}, { "$set" : { "state" : User.USER_DRV_TRAVELING} } ) 
		users.update( { "_id" : passenger["_id"] }, { "$set" : { "state" : User.USER_PSG_TRAVELING} } ) 

		trip = list(active_trips.find({"_id" : trip["_id"]}))[0]
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
		user = user[0]

		#dist = Distances.computeDistance(user["coord"], trip["directions"]["origin"])
		#logger.getLogger().debug("Distance from user [" + user["username"] + "] to starting point is " + str(dist))
		#if dist > MAXIMUM_USER_DISTANCE:
		#		return ResponseMaker.response_error(constants.PARAMERR, "Bad request - you are too far away from the starting point")

		# Anyone can accept first
		if trip["state"] == TripStates.TRIP_CONFIRMED:
			return self.start_handler_any(action, trip, user)
		elif trip["state"] == TripStates.TRIP_STARTED_DRIVER:
			return self.start_handler_passenger(action, trip, user)
		elif trip["state"] == TripStates.TRIP_STARTED_PASSENGER:
			return self.start_handler_driver(action, trip, user)

		return ResponseMaker.response_error(constants.PARAMERR, "Internal server error.")


	def finish_handler_any(self, action, trip, user):
		users = MongoController.getCollection("online")
		active_trips = MongoController.getCollection("active_trips")

		if user["type"] == User.USER_TYPE_PASSENGER:
			if user["state"] != User.USER_PSG_TRAVELING:
				return ResponseMaker.response_error(constants.PARAMERR, "Bad request - passenger is not traveling")
			trip_state = TripStates.TRIP_FINISHED_PASSENGER
			user_state = User.USER_PSG_WAITING_FINISH
			theother = list(users.find({ "_id" : trip["driverId"]}))[0]


		if user["type"] == User.USER_TYPE_DRIVER:
			if user["state"] != User.USER_DRV_TRAVELING:
				return ResponseMaker.response_error(constants.PARAMERR, "Bad request - driver is not traveling")
			trip_state = TripStates.TRIP_FINISHED_DRIVER
			user_state = User.USER_DRV_WAITING_FINISH
			theother = list(users.find({ "_id" : trip["passengerId"]}))[0]

		active_trips.update( { "_id" : trip["_id"] }, { "$set" : { "state" : trip_state } } )
		users.update( { "_id" : user["_id"] }, { "$set" : { "state" : user_state } } ) 

		NotificationSender().notifyUser(theother["username"], user["username"] + " wants to finish the trip!")

		return ResponseMaker.response_object(constants.SUCCESS, ["message", "action", "trip"], ["Trip was updated.", action["action"], trip])

	def finish_handler_passenger(self, action, trip, user):
		users = MongoController.getCollection("online")
		active_trips = MongoController.getCollection("active_trips")
		if user["state"] != User.USER_PSG_TRAVELING:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - passenger is not traveling")

		driver = list(users.find({ "_id" : trip["driverId"]}))[0]
		if driver["state"] != User.USER_DRV_WAITING_FINISH:
			return ResponseMaker.response_error(constants.ERROR, "Internal server error - driver in a bad state")

		active_trips.update( { "_id" : trip["_id"] }, { "$set" : { "state" : TripStates.TRIP_FINISHED } } )
		active_trips.update( { "_id" : trip["_id"] }, { "$set" : { "time_finish" :  datetime.datetime.now().isoformat() } } )
		users.update( { "_id" : user["_id"] }, { "$set" : { "state" : User.USER_PSG_ARRIVED } } ) 
		users.update( { "_id" : driver["_id"] }, { "$set" : { "state" : User.USER_DRV_IDLE } } ) 
		users.update( { "_id" : driver["_id"] }, { "$set" : { "tripId" : "" } } ) 
		return ResponseMaker.response_object(constants.SUCCESS, ["message", "action", "trip"], ["Trip just started.", action["action"], trip])

	def finish_handler_driver(self, action, trip, user):
		users = MongoController.getCollection("online")
		active_trips = MongoController.getCollection("active_trips")
		if user["state"] != User.USER_DRV_TRAVELING:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - driver is not traveling")

		passenger = list(users.find({ "_id" : trip["passengerId"]}))[0]
		if passenger["state"] != User.USER_PSG_WAITING_FINISH:
			return ResponseMaker.response_error(constants.ERROR, "Internal server error - passenger in a bad state")

		active_trips.update( { "_id" : trip["_id"] }, { "$set" : { "state" : TripStates.TRIP_FINISHED } } )
		active_trips.update( { "_id" : trip["_id"] }, { "$set" : { "time_finish" :  datetime.datetime.now().isoformat() } } )
		users.update( { "_id" : user["_id"]}, { "$set" : { "state" : User.USER_DRV_IDLE } } ) 
		users.update( { "_id" : user["_id"]}, { "$set" : { "tripId" : "" } } ) 
		users.update( { "_id" : passenger["_id"] }, { "$set" : { "state" : User.USER_PSG_ARRIVED } } ) 
		return ResponseMaker.response_object(constants.SUCCESS, ["message", "action", "trip"], ["Trip just started.", action["action"], trip])


	def finish_handler(self, action, trip, userId):
		if not userId == trip["passengerId"] and not userId == trip["driverId"]:
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden - you are not part of this trip")
	
		if trip["state"] not in TripStates.TRIP_FINISH_VALID:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - trip is not started")

		# Retrieve user
		users = MongoController.getCollection("online")
		user = list(users.find({"_id" : userId}))
		if len(user) > 1:
			return ResponseMaker.response_error(constants.ERROR, "Internal server error - more than one user with same ID.")
		if len(user) == 0:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - user not found")
		user = user [0]

		# Anyone can finish first
		if trip["state"] == TripStates.TRIP_STARTED:
			return self.finish_handler_any(action, trip, user)
		elif trip["state"] == TripStates.TRIP_FINISHED_DRIVER:
			return self.finish_handler_passenger(action, trip, user)
		elif trip["state"] == TripStates.TRIP_FINISHED_PASSENGER:
			return self.finish_handler_driver(action, trip, user)

		return ResponseMaker.response_error(constants.PARAMERR, "Internal server error.")



	def rate_handler(self, action, trip, userId):
		if not userId == trip["passengerId"]:
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden - you were not the passenger of this trip")

		if not trip["state"] == TripStates.TRIP_FINISHED:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - this trip cannot be rated")
		
		if action["rating"] > 5 or action["rating"] < 0:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - thats not a valid rating")

		# Retrieve driver
		users = MongoController.getCollection("online")
		passenger = list(users.find({"_id" : userId}))[0]
		driver = list(users.find({"_id" : trip["driverId"]}))[0]

		if not passenger["state"] == User.USER_PSG_ARRIVED:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - wrong passenger state")

		active_trips = MongoController.getCollection("active_trips")
		active_trips.update( { "_id" : trip["_id"] }, { "$set" : { "state" : TripStates.TRIP_FINISHED_RATED } } )
		rating_count = driver["rating"]["rateCount"] + 1
		current_rate = driver["rating"]["rate"] + action["rating"]
		logger.getLogger().debug("User [" + str(passenger["_id"]) + "] rated with " + str(action["rating"]) + " driver [" + str(driver["_id"]) + "]")
		users.update( { "_id" : driver["_id"] }, { "$set" : { "rating.rateCount" : rating_count } } )
		users.update( { "_id" : driver["_id"] }, { "$set" : { "rating.rate" : current_rate } } )
		
		NotificationSender().notifyUser(driver["username"], "You just got a new review!")

		return ResponseMaker.response_object(constants.SUCCESS, ["message", "action", "trip"], ["Rating saved.", action["action"], trip])

	def payment_handler(self, action, trip, userId):
		if not userId == trip["passengerId"]:
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden - you were not the passenger of this trip")

		if not trip["state"] in TripStates.TRIP_ABLE_TO_PAY:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - this trip cannot be payed yet")

		shared_trip = { "trip" : TripStates.trip_to_shared(trip), "paymethod" : action["paymethod"] }
		try:
			(status_code, response) = ServerRequest.createTrip(shared_trip)
		except Exception as e:	
			logger.getLogger().exception(str(e))
			print(str(e))
			return ResponseMaker.response_error(500, "Internal Error")

		
		logger.getLogger().exception(shared_trip)
		if not status_code == constants.CREATE_SUCCESS:
			return ResponseMaker.response_object(status_code, ["message", "to_shared"],  ["Payment API error, try again", shared_trip])

		active_trips = MongoController.getCollection("active_trips")
		active_trips.update( { "_id" : trip["_id"] }, { "$set" : { "state" : TripStates.TRIP_PAYED } } )
		active_trips.remove( { "_id" : trip["_id"] } )

		users = MongoController.getCollection("online")
		users.update( { "_id" : userId }, { "$set" : { "state" : User.USER_PSG_IDLE} } )
		users.update( { "_id" : userId }, { "$set" : { "tripId" : "" } } )

		return ResponseMaker.response_object(status_code, ["paymethod"], [response]) 
