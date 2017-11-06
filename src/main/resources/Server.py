"""@package Server
This module contains all the handlers for /server/ping endpoint.
Should allow the user to verify that the AppServer is alive.
"""

from flask_restful import Resource
from flask import jsonify, abort, request, make_response
from src.main.com import ResponseMaker, ServerRequest, TokenGenerator

from src.main.mongodb import MongoController
import config.constants as constants

import os
import requests
import logging as logger

class Server(Resource):

	def get(self):
		raise NotImplemented
