"""@package Server
This module contains all the handlers for /server/ping endpoint.
Should allow the user to verify that the AppServer is alive.
"""
import os
import json
import requests
import logging as logger
import config.constants as constants

headers = {'Content-Type' : 'application/json'}

SS_URI = "http://127.0.0.1:5000/api" #'https://fiuber-shared-server.herokuapp.com/api'
if not "SS_URL" in os.environ:
	os.environ["SS_URL"] = SS_URI

DEFAULT_APP_TOKEN="Sorry there is no token"

if not "APP_TOKEN" in os.environ:
	os.environ["APP_TOKEN"] = DEFAULT_APP_TOKEN

QUERY_TOKEN = "?token=" + os.environ["APP_TOKEN"]

SERVER_END = "/server"

class ServerTokenUpdater(object):
	
	def __call__(self, f):
		def wrapped_f(*args):
			status, res = f(*args)
			if (status == constants.UNAUTHORIZED):
				self.updateToken()
			return f(*args)
		return wrapped_f	

	"""Updates the current App-Server token to communicate with Shared-Server.
	Returns a json structure containing server information, with the following layout:
	    {
	      "id": "serverId",
	      "_ref": "reference",
	      "createdBy": "string",
	      "createdTime": 0,
	      "name": "string",
	      "lastConnection": 0
	    }
	"""
	def updateToken(self):
		try:
			status, request = self.pingServer()
			print (status, request)
			if (status != constants.SUCCESS):
				logger.getLogger().error("Shared Server returned error code {}.".format(status))
				return {"error" : status}
			token = request["token"]
			os.environ["APP_TOKEN"] = token["token"]
			logger.getLogger().debug("Successfully updated App Server Token.")
			return request["server"]
		except Exception, e:
			logger.getLogger().error("Unexpected Error." + str(e))
			return {"error" : str(e)}

	
	"""Returns a json object with the following layout:
	  "ping": {
	    "server": {
	      "id": "string",
	      "_ref": "string",
	      "createdBy": "string",
	      "createdTime": 0,
	      "name": "string",
	      "lastConnection": 0
	    },
	    "token": {
	      "expiresAt": 0,
	      "token": "string"
	    }
	 }
	"""
	def pingServer(self):
		r = requests.get(os.environ["SS_URL"] + SERVER_END + "/ping" + QUERY_TOKEN, headers=headers)
		if (r.status_code != constants.SUCCESS):
			logger.getLogger("Shared Server returned error: %d"%(r.status_code))
			return (r.status_code, r.json())		
		return (r.status_code, r.json()["ping"])


	

