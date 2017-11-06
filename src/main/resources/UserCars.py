"""@package UserCars
This module contains all the handlers for /users/<int:userId>/cars and /users/<int:userId>/cars/<int:carId> endpoints.
Should allow all CRUD operations over user cars with validation of credentials.
"""

from flask_restful import Resource
from flask import jsonify, abort, request, make_response
from src.main.com import ResponseMaker, ServerRequest, TokenGenerator

from src.main.mongodb import MongoController
import config.constants as constants

import os
import requests
import logging as logger

class Cars(Resource):

	def __init__(self):
		self.users = MongoController.getCollection("online")

	"""Receives a userId and returns a list of all the cars owned by that user, with the following layout:
		{	
		  "cars": [{
                      "id": "idCar1",
                      "_ref": "refCar1",
                      "owner": "ownerCar1",
                      "properties": [{
                        "name": "nameCar1",
                        "value": "valueCar1"
                      }]
                  }]
		}		
	"""
	def get(self, id):
		logger.getLogger().debug("GET at /users/userId/cars " + str(id))
		if not "UserToken" in request.headers:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing token")

		token = request.headers['UserToken']

		(valid, decoded) = TokenGenerator.validateToken(token)

		print(decoded)
		if not valid or (decoded['_id'] != id):
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden")
		
		cars = [user for user in self.users.find() if user['_id'] == id and user['type'] == 'driver']

		try:
			if (len(cars) == 0):
				print("FETECHING CARS...")
				status_code, cars = ServerRequest.getUserCars(id)
		except Exception, e:
			return ResponseMaker.response_error(constants.NOT_FOUND, "User id did not match any existing users.")			
		return ResponseMaker.response_object(constants.SUCCESS, ['cars'], cars)
	
	"""Receives a user id. Creates a car associated to the identified user with the information
	provided for the car, which must have the following layout:
	{
	  'name': 'brandName',
	  'value': 'plateNumber'
	}		
	"""
	def post(self, id):
		print(request.json)
		logger.getLogger().debug("POST at /users/cars")
		logger.getLogger().debug(request.json)
		
		try:

			if not "UserToken" in request.headers:
				return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing token")

			token = request.headers['UserToken']

			(valid, decoded) = TokenGenerator.validateToken(token)

			print(decoded)
			if not valid or (decoded['_id'] != id):
				return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden")

			#Create car at shared server.
			(status, response) = ServerRequest.createUserCar(id, request.json)
		
			if (status != constants.CREATE_SUCCESS):
				return ResponseMaker.response_error(status, response["message"])
			#TODO:Update local database
			car = response
			car["_id"] = car.pop("id")
			#self.users.update({"_id": id}, { $push: { "cars": car } })
			return ResponseMaker.response_object(status, ["car"], [car])

		except Exception, e:
			return ResponseMaker.response_error(constants.ERROR, "Unexpected error")			

class CarsById(Resource):
	"""This class initializes a resource named CarsById which allows
	the user to perform operations Consult(GET), Update(PUT) and Removal(DELETE)
	through user and car ids.
	"""		

	def __init__(self):
		self.users = MongoController.getCollection("online")

	def get(self, userId, carId):
		logger.getLogger().debug("GET at /users/"+str(userId)+"/carId/" + str(carId))
		if not "UserToken" in request.headers:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing token")

		token = request.headers['UserToken']

		(valid, decoded) = TokenGenerator.validateToken(token)

		print(decoded)
		if not valid or (decoded['_id'] != userId):
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden")
		
		car = []#[ car for car in self.users.find( { $and: [ { "_id": { $eq : userId} }, { "cars._id": { $eq : carId } } ] } , { cars : 1 } ) if car["_id"]==carId ]
		
		try:
			if (len(car) == 0):
				status_code, car = ServerRequest.getUserCar(userId, carId)
			return ResponseMaker.response_object(constants.SUCCESS, ['car'], car["properties"])
		except Exception, e:
			return ResponseMaker.response_error(constants.ERROR,  "Unexpected error")			
		
		
	def put(self, userId, carId):
		print(userId)
		logger.getLogger().debug("PUT at /users/" + str(userId) + "/cars/" + str(carId))

		if not "UserToken" in request.headers:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing token")

		token = request.headers['UserToken']
		(valid, decoded) = TokenGenerator.validateToken(token)

		if not valid or (decoded['_id'] != userId):
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden")
		try:
			#Ask Shared-Server to update this user
			success, updated_car = ServerRequest.updateUserCar(userId, carId, request.json)	
			if success:
				#TODO:Update in local data-base
				#self.users.update(...)
				logger.getLogger().info("Successfully updated user")
				return ResponseMaker.response_error(constants.SUCCESS, "User updated successfully!")
			return ResponseMaker.response_error(constants.NOT_FOUND, "User not found!")	
		except ValueError as e:
			logger.getLogger().error(str(e))
			return ResponseMaker.response_error(constants.UPDATE_CONFLICT, "User update failed:" + str(e))
		except requests.exceptions.Timeout as e:	
			logger.getLogger().error(str(e))	
			return ResponseMaker.response_error(constants.REQ_TIMEOUT, "User update failed:" + str(e))
		except Exception as e:
			logger.getLogger().error(str(e))
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden: " + str(e))		

	def delete(self, userId, carId):
		print("DELETE at /users/id")
		logger.getLogger().debug("DELETE at /users/" + str(userId) + "/cars/" + str(carId))

		if not "UserToken" in request.headers:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing token")

		token = request.headers['UserToken']

		(valid, decoded) = TokenGenerator.validateToken(token)

		print(decoded)
		if not valid or (decoded['_id'] != userId):
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden")
		try:
			#Ask Shared-Server to delete this user
			delete_success, status_code = ServerRequest.deleteUserCar(userId, carId)
			if delete_success:
				#TODO:Delete in local data-base
				#deletedCar = [car for user in self.users.find() for car in user["cars"] if (user['_id'] == userId and car["_id"]==carId)]
				#self.users.update({"_id": id}, { $pop: { "cars.id": carId } })
				logger.getLogger().info("Successfully deleted user car.")			
				return ResponseMaker.response_object(constants.DELETE_SUCCESS, ['car'], {"id":carId})			
			else:
				logger.getLogger().error("Attempted to delete car with non-existent id.")
				return ResponseMaker.response_error(status_code, "Delete error")	

		except Exception, e:
			return ResponseMaker.response_error(constants.ERROR, "Unexpected error")			


