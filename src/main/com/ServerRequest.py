"""@package ServerRequest
Implements API methods that allow user related
transactions and requests to be sent to the Shared 
Server.
"""

import logging as logger
#import config.constants as constants

#USER_END = constants.SS_URI + "/users"
#CARS = "/cars"
#TRANSACT_ENDPOINT = "/transactions"
#TRIPS_ENDPOINT = "/trips"

#headers = {'Content-Type' : 'application/json'}
#MAX_ATTEMPTS = 10

""" Asks shared server to validate user credentials"""
def validateUser(user_js):
	if user_js['password'] == "1234":
		logger.getLogger().debug("User found!!")
		return { "_id" : 1, "username" : "juan", "birthdate": "18/07/1994", "firstname" : "Juan"}
	else:
		logger.getLogger().debug("User no valid!!")
		return None 

#"""Returns a list of all the users and their information in json format."""
#def getUsers():
#	r = requests.get(USER_END)
#	if (r.status_code != constants.SUCCESS):
#		raise Exception("Shared Server returned error: %d"%(r.status_code))
#	return request.get_json()['users']

#"""Attempts to perform a request. If the request is rejected because of a reference missmatch, the 
#operation will be repeated until successfully completed or until a maximum number of attempts is 
#reached or until another error arises."""
#def _permformRequest(f, endpoint, updatedEntityName, updatedEntity):
#	r = f(endpoint, updatedEntity)
#	attempts = 0
#	try:
#		while (r.status_code == constants.UPDATE_CONFLICT) and (attempts < MAX_ATTEMPTS):
#			newData = json.loads(requests.get(endpoint).text)
#			updatedEntity["_ref"] = newData[updatedEntityName][0]["_ref"]
#			r = f(endpoint, updatedEntity)
#			attempts += 1
#		if (r.status_code == constants.UPDATE_CONFLICT):
#			logger.getLogger().error("Attempted to update user. Request failed with reference error.")
#			raise ValueError("Error attempting to update entity. Try again later.")
#	except requests.exceptions.Timeout:
#		logger.getLogger().error("Attempted to update user. Request timed-out")	
#	return r

#"""Receives a user represented by a json structure and attempts to update its data.
#Returns False if the user id does not match any user id or _ref value is invalid.
#Returns True if the user info was successfully updated."""
#def updateUser(user_js):
#	endpoint = USER_END  + "?userId=" + user["user"]["id"]
#	r = Users._permformRequest(lambda ep, u: requests.put(ep, json.dumps(u), headers=headers), endpoint, "users", user_js)
#	if (r.status_code == constants.NOT_FOUND):
#		return False
#	if (r.status_code != constants.SUCCESS):
#		raise Exception("Shared Server returned error: %d"%(r.status_code))
#	return True


""" Asks shared server to create a nes user"""
def createUser(user_js):
	pass
#	r = requests.post(Users.endpoint, data = json.dumps(user_js), headers=headers)
#	if (r.status_code != CREATE_SUCCESS):
#		raise Exception("Shared Server returned error: %d"%(r.status_code))
#	return request.get_json()['user']



