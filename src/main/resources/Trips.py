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
		raise NotImplemented
	
class UserTrips(Resource):

	def get(self, id):
		raise NotImplemented

class TripEstimation(Resource):

	def post(self):
		raise NotImplemented


class TripsById(Resource):

	def get(self):
		raise NotImplemented


