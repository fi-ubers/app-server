"""@package Directions
This modules provides some Google Direction wrappers presented at /directions
endpoint. It is meant to allow clientes find routes for their trips.
"""

from flask_restful import Resource
from flask import jsonify, abort, request, make_response
from src.main.com import ResponseMaker, TokenGenerator

import config.constants as constants
import os
import logging as logger
import requests

GOOGLE_API_KEY = "AIzaSyD5nKGS9WOqJI0kN9s24aP27Axuq6WuW0A"
GOOGLE_DIRECTIONS = "https://maps.googleapis.com/maps/api/directions/json"

class Directions(Resource):


	def convert_response(self, gresp):
		directions = {}
		directions["status"] = gresp["status"]
		directions["origin"] = gresp["routes"][0]["legs"][0]["start_location"]
		directions["origin_name"] = gresp["routes"][0]["legs"][0]["start_address"]
		directions["destination"] = gresp["routes"][0]["legs"][0]["end_location"]
		directions["destination_name"] = gresp["routes"][0]["legs"][0]["end_address"]
		directions["distance"] = gresp["routes"][0]["legs"][0]["distance"]["value"]
		directions["duration"] = gresp["routes"][0]["legs"][0]["duration"]["value"]

		directions["path"] = []
		for waypoint in gresp["routes"][0]["legs"][0]["steps"]:
			aux = {}
			aux["distance"] = waypoint["distance"]["value"]
			aux["duration"] = waypoint["duration"]["value"]
			aux["coords"] = waypoint["end_location"]
			directions["path"].append(aux)

		return directions

	def post(self):
		logger.getLogger().debug("POST at /directions")
		logger.getLogger().debug(request.json)
		print(request.json)

		# Check user validity
		if not "UserToken" in request.headers:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing token")
		token = request.headers['UserToken']
		(valid, decoded) = TokenGenerator.validateToken(token)
		if not valid:
			return ResponseMaker.response_error(constants.FORBIDDEN, "Forbidden")

		# Check endpoints are in the request 
		if not request.json:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request - missing parameters")
		if not "origin" in request.json or not "destination" in request.json:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request")
		origin = request.json['origin']
		destination = request.json['destination']

		# Check for coordinates on endpoints
		if not "lat" in origin or not "lng" in origin:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request")
		if not "lat" in destination or not "lng" in destination:
			return ResponseMaker.response_error(constants.PARAMERR, "Bad request")


		origin_str = "origin=" + str(origin["lat"]) + "," + str(origin["lng"])
		print("origin_str = " + origin_str)
		destination_str = "destination=" + str(destination["lat"]) + "," + str(destination["lng"])
		
		r = requests.get(GOOGLE_DIRECTIONS + "?" + origin_str + "&" + destination_str + "&key=" + GOOGLE_API_KEY)

		r = r.json()
		print(r)

		if r["status"] != "OK":
			return ResponseMaker.response_error(500, "Google API error: " + r["status"])
		
		return ResponseMaker.response_object(200, ["directions"], [self.convert_response(r)])
