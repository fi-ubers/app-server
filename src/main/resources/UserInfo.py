"""@package UserInfo
This module contains all the handlers for /users/id/location and /users/id/rating endpoints.
Should allow viewing and modification of user information with validation of credentials.
"""

from flask_restful import Resource
from flask import jsonify, abort, request, make_response
from src.main.com import ResponseMaker, ServerRequest, TokenGenerator
from src.main.mongodb import MongoController
from src.main.model import User
import config.constants as constants

import os
import requests
import logging as logger

class LocUserById(Resource):
	"""This class initializes a resource named LocUserById which allows
	the user to perform operations Consult(GET) and Update(PUT) on user location
	through	the user id.
	"""
	def __init__(self):
		self.users = MongoController.getCollection("online")

	"""Returns a JSON specifying a user's location with the following layout:
	'user_loc':{
		'_id':'0',
		'online':False,
		'coord': {
			'lat':0,
			'lng':0
		}
	}
	"""
	def get(self, id):
		logger.getLogger().debug("GET at /users/" + str(id) + "/location")
		if not "UserToken" in request.headers:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing token")

		token = request.headers['UserToken']

		(valid, decoded) = TokenGenerator.validateToken(token)

		if not valid or (decoded['_id'] != id):
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden")

		print("GET at /users/" + str(id) + "/location")
		candidates = [user for user in self.users.find() if user['_id'] == id]

		if len(candidates) == 0:
			#If not available in local data-base, ask Shared-Server for user info.
			(status, response) = ServerRequest.getUser(id)

			if (status != constants.SUCCESS):
				return ResponseMaker.response_error(status, response["message"])

			candidates = [ response ]
			user = candidates[0]
			self.users.insert_one(user)

		if len(candidates) == 0:
			logger.getLogger().error("Attempted to retrieve user with non-existent id.")
			return ResponseMaker.response_error(constants.NOT_FOUND, "User id not found:" + str(e))

		return ResponseMaker.response_object(constants.SUCCESS, ['user_loc'], [User.LocUserJSON(candidates[0])])

	"""Receives a JSON specifying a user's new location with the following layout:
		'coord': {
			'lat':0,
			'lng':0
		}
	Updates the user's location to specified coordinates.	
	"""
	def put(self, id):
		print(id)
		print("PUT at /user/" + str(id) + "/loacation")
		logger.getLogger().debug("PUT at /users/" + str(id) + "/location")

		if not "UserToken" in request.headers:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing token")

		token = request.headers['UserToken']
		(valid, decoded) = TokenGenerator.validateToken(token)

		if not valid or (decoded['_id'] != id):
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden")
		try:
			updated_location = request.json["coord"]
			#Update in local data-base
			self.users.update({'_id':id}, {"$set":{"coord":updated_location}},  upsert= True)
			logger.getLogger().info("Successfully updated user location")
			return ResponseMaker.response_object(constants.SUCCESS, ['location'], [updated_location])
		except ValueError as e:
			logger.getLogger().error(str(e))
			return ResponseMaker.response_error(constants.UPDATE_CONFLICT, "User update failed:" + str(e))
		except requests.exceptions.Timeout as e:
			logger.getLogger().error(str(e))
			return ResponseMaker.response_error(constants.REQ_TIMEOUT, "User update failed:" + str(e))
		except Exception as e:
			logger.getLogger().error(str(e))
			return ResponseMaker.response_error(constants.ERROR, str(e))

class UserRatingById(Resource):

	"""This class initializes a resource named LocUserById which allows
	the user to perform operations Consult(GET) and Update(PUT) on user location
	through	the user id.
	"""
	def __init__(self):
		self.users = MongoController.getCollection("online")

	"""Returns a JSON specifying a driver's rating score with the following layout:
	'rating':{
		'rate':0,
		'rateCount':0
	}
	"""
	def get(self, id):
		logger.getLogger().debug("GET at /users/" + str(id) + "/rating")
		if not "UserToken" in request.headers:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing token")

		token = request.headers['UserToken']

		(valid, decoded) = TokenGenerator.validateToken(token)

		if not valid or (decoded['_id'] != id):
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden")
		
		try:
			print("GET at /users/" + str(id) + "/rating")
			candidates = [user for user in self.users.find() if user['_id'] == id]

			if len(candidates) == 0:
				#If not available in local data-base, ask Shared-Server for user info.
				(status, response) = ServerRequest.getUser(id)
				if (status != constants.SUCCESS):
					return ResponseMaker.response_error(status, response["message"])
				candidates = [ response ]
				
			if len(candidates) == 0:
				logger.getLogger().error("Attempted to retrieve user with non-existent id.")
				return ResponseMaker.response_error(constants.NOT_FOUND, "User id not found:" + str(e))

			if candidates[0]["type"] != "driver":
				return ResponseMaker.response_error(constants.PARAMERR, "The requested user is not a driver. Only drivers receive ratings.")
			return ResponseMaker.response_object(constants.SUCCESS, ['rating'], [User.RatingUserJSON(candidates[0])])

		except Exception as e:
			logger.getLogger().error(str(e))
			return ResponseMaker.response_error(constants.ERROR, str(e))

	"""Receives a JSON specifying a driver's new rating with the following layout:
	'rating':{
		'rate':0,
		'rateCount':0
	}
	Averages the 
	"""
	def put(self, id):
		print(id)
		print("PUT at /user/" + str(id) + "/rating")
		logger.getLogger().debug("PUT at /users/" + str(id) + "/rating")

		if not "UserToken" in request.headers:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing token")

		token = request.headers['UserToken']
		(valid, decoded) = TokenGenerator.validateToken(token)

		if not valid or (decoded['_id'] != id):
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden")
		try:
			new_score = request.json["rate"]
			rating_count = [user["rating"]["rateCount"] for user in self.users.find() if user['_id'] == id and user['type'] == "driver"][0]
			current_rate = [user["rating"]["rate"] for user in self.users.find() if user['_id'] == id and user['type'] == "driver"][0]			
			if len(rating_count) == 0 and len(current_rate) == 0:
				return ResponseMaker.response_error(constants.NOT_FOUND, "User id not found.")
			#Recalculate rating
			rating_count += 1
			current_rate = current_rate + new_score
			#Update in local data-base
			self.users.update({'_id':id}, {"$set":{"rating.rateCount": rating_count, "rating.rate": current_rate} },  upsert= True)
			logger.getLogger().info("Successfully updated driver rating")

			driver = [user for user in self.users.find() if user['_id'] == id and user['type'] == "driver"][0]			
			return ResponseMaker.response_object(constants.SUCCESS, ['rating'], [User.RatingUserJSON(driver)])
		except ValueError as e:
			logger.getLogger().error(str(e))
			return ResponseMaker.response_error(constants.UPDATE_CONFLICT, "User update failed:" + str(e))
		except requests.exceptions.Timeout as e:
			logger.getLogger().error(str(e))
			return ResponseMaker.response_error(constants.REQ_TIMEOUT, "User update failed:" + str(e))
		except Exception as e:
			logger.getLogger().error(str(e))
			return ResponseMaker.response_error(constants.ERROR, str(e))


