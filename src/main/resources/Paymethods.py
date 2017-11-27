"""@package Paymethods
This module contains all the handlers for /payment endpoint.
Should allow the user to consult all available paymethods.
"""

import os
import requests
import logging as logger
from flask_restful import Resource
from flask import jsonify, abort, request, make_response
from src.main.model import TripStates
from src.main.mongodb import MongoController
import config.constants as constants
from src.main.com import ResponseMaker, ServerRequest, TokenGenerator
from src.main.com.NotificationManager import NotificationSender


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

	""" Handler to get a list of all users.
	Requieres: user token in the header.
		UserToken : string
	Requires trip and payment information:
	  "trip": {
	    "_id": "string",
	    "applicationOwner": "string",
	    "driverId": "string",
	    "passengerId": "string",
	    "start": {
	      "address": {
		"street": "string",
		"location": {
		  "lat": 0,
		  "lon": 0
		}
	      },
	      "timestamp": 0
	    },
	    "end": {
	      "address": {
		"street": "string",
		"location": {
		  "lat": 0,
		  "lon": 0
		}
	      },
	      "timestamp": 0
	    },
	    "totalTime": 0,
	    "waitTime": 0,
	    "travelTime": 0,
	    "distance": 0,
	    "route": [
	      {
		"location": {
		  "lat": 0,
		  "lon": 0
		},
		"timestamp": 0
	      }
	    ],
	    "cost": {
	      "currency": "string",
	      "value": 0
	    }
	  },
	  "paymethod": {
	    "paymethod": "string",
	    "parameters": {}
	  }
	"""
	def post(self):
		logger.getLogger().debug("POST at /payment")
		# (validate-token) Validate user token
		if not "UserToken" in request.headers:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing token")

		users = MongoController.getCollection("online")
		active_trips = MongoController.getCollection("active_trips")

		payment_info = request.json
		trip = list(active_trips.find({"_id" : payment_info["trip"]["_id"]}))	
		
		if len(trip) == 0:
			return ResponseMaker.response_error(constants.NOT_FOUND, "Error - this trip has no pending payment.")	
		if payment_info["passengerId"] != trip["passengerId"]:
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden - you are not the owner of this trip.")
		if trip["state"] != TripStates.TRIP_FINISHED:
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden - this trip has not concluded.")
		try:
			status_code, response = ServerRequest.makePayment(trip["passengerId"],payment_info)		
			if status_code == constants.SUCCESS:
				transaction = response
				active_trips.delete({"_id":trip["_id"]})
				users.update({"_id":trip["passengerId"]}, {"$set":{"state":User.USER_PSG_IDLE, "tripId" : "" }})
				users.update({"_id":trip["driverId"]}, {"$set":{"state":User.USER_DRV_IDLE, "tripId" : "" }})
				NotificationSender.notifyUser(trip["passengerId"], "Your payment was successfully processed. Thank you for choosing FIUBER.")
				logger.getLogger().debug("Trip " + str(trip["_id"]) + "successfully paid.")
				return ResponseMaker.response_object(constants.SUCCESS, ["transaction"], transaction)	
			logger.getLogger().error("ERROR ocurred when attempting to pay trip: " + str(trip["_id"]))
			return ResponseMaker.response_error(constants.ERROR, "This transaction was unsuccessful. " + str(response["message"]))			
		except Exception as e:	
			return ResponseMaker.response_error(constants.ERROR, "Error - an error ocurred during this transaction.")


