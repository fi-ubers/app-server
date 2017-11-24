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
SS_URI = 'https://fiuber-shared-server.herokuapp.com/api'#"http://127.0.0.1:5000/api"
if not "SS_URL" in os.environ:
	os.environ["SS_URL"] = SS_URI

DEFAULT_APP_TOKEN ='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MzQsImp0aSI6ImE3YWIxOTA2LWQwZjEtNDY1Ny05OTc4LTdiYjBmODJhZjZhOSIsImlhdCI6MTUwODI2MDQ4OX0.IrurkKZ-wbmTp8kQf_rGVHv5jcvwCibQJDoHwvZJ1Gg'

if not "APP_TOKEN" in os.environ:
	os.environ["APP_TOKEN"] = DEFAULT_APP_TOKEN

QUERY_TOKEN = "?token="
SERVER_END = "/server"

class ServerTokenUpdater(object):
	
	def __call__(self, f):
		def wrapped_f(*args):
			status, res = f(*args)
			if (status == constants.UNAUTHORIZED):
				self.updateToken()
				return f(*args)
			return status, res
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
			status_code, request = self.pingServer()
			print (status_code, request)
			if (status_code != constants.SUCCESS):
				logger.getLogger().error("Shared Server returned error code {}.".format(status_code))
				return {"error" : status_code}
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
		r = requests.get(os.environ["SS_URL"] + SERVER_END + "/ping" + QUERY_TOKEN + os.environ["APP_TOKEN"], headers=headers)
		if (r.status_code != constants.SUCCESS):
			logger.getLogger("Shared Server returned error: %d"%(r.status_code))
			return (r.status_code, r.json())		
		return (r.status_code, r.json()["ping"])





