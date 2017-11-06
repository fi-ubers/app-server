"""@package Paymethods
This module contains all the handlers for /payment endpoint.
Should allow the user to consult all available paymethods.
"""

from flask_restful import Resource
from flask import jsonify, abort, request, make_response
from src.main.com import ResponseMaker, ServerRequest, TokenGenerator

from src.main.mongodb import MongoController
import config.constants as constants

import os
import requests
import logging as logger

class Paymethods(Resource):

	def get(self):
		raise NotImplemented
