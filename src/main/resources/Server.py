"""@package Server
This module contains all the handlers for /server/ping endpoint.
Should allow the user to verify that the AppServer is alive.
"""
import os
import logging as logger
from src.main.com import ServerRequest
import config.constants as constants

class ServerConn(object):
	
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
			status, request = ServerRequest.pingServer()
			print (status, request)
			if (status != constants.SUCCESS):
				logger.getLogger().error("Shared Server returned error code {}.".format(status))
				return {"error" : status}
			token = request["token"]
			os.environ["APP_TOKEN"] = token["token"]
			logger.getLogger().debug("Successfully updated App Server Token.")
			return request["server"]
		except Exception as e:
			logger.getLogger().error("Unexpected Error." + str(e))
			return {"error" : str(e)}

	


