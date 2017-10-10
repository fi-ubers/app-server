"""@package ServerRequest
Implements API methods that allow user related
transactions and requests to be sent to the Shared 
Server.
"""
import os
import json
import requests
import logging as logger
import config.constants as constants

if not "SS_URL" in os.environ:
	os.environ["SS_URL"] = constants.SS_URI

APP_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwianRpIjoiNTZhYWVlZWMtNGQ1Yy00NjEwLTgwMzYtN2EwYTA3YTViYzAyIiwiZXhwIjoxNTA4MDk1NzQ2LCJpYXQiOjE1MDc2NjU2Njd9.4V3AAWuex2wCZJYdePm-k8Xp8yQYVYp8imBOlCVMDEs'
USER_END = os.environ["SS_URL"] + "/users" 
QUERY_TOKEN = "?token=" + APP_TOKEN
#CARS = "/cars"
#TRANSACT_ENDPOINT = "/transactions"
#TRIPS_ENDPOINT = "/trips"

headers = {'Content-Type' : 'application/json'}
MAX_ATTEMPTS = 10

#""" Asks shared server to validate user credentials"""
#def validateUser(user_js):
#	if user_js['password'] == "1234":
#		logger.getLogger().debug("User found!!")
#		return { "_id" : 1, "username" : "juan", "birthdate": "18/07/1994", "firstname" : "Juan"}
#	else:
#		logger.getLogger().debug("User no valid!!")
#		return None 

"""Returns a list of all the users and their information in json format."""
def getUsers():
	r = requests.get(USER_END + QUERY_TOKEN, headers=headers)
	if (r.status_code != constants.SUCCESS):
		logger.getLogger("Shared Server returned error: %d"%(r.status_code))
		raise Exception("Shared Server returned error: %d"%(r.status_code))
	return r.json()["users"]


"""Receives a user id. Returns the information of the user that matches that id in json format.
"""
def getUser(userId):
	r = requests.get(USER_END + "/" + str(userId) + QUERY_TOKEN, headers=headers)

	if (r.status_code != constants.SUCCESS):
		logger.getLogger("Shared Server returned error: %d"%(r.status_code))
		return (r.status_code, r.json());

	return (r.status_code, r.json()["user"])


"""Attempts to perform a request. If the request is rejected because of a reference missmatch, the 
operation will be repeated until successfully completed or until a maximum number of attempts is 
reached or until another error arises."""
def _permformUpdate(f, endpoint, updatedEntityName, updatedEntity):
	r = f(endpoint, updatedEntity)
	attempts = 0
	while (r.status_code == constants.UPDATE_CONFLICT) and (attempts < MAX_ATTEMPTS):
		print ("UPDATE FAILED, RETRYING...")
		newData = json.loads(requests.get(endpoint, headers=headers).text)
		updatedEntity["_ref"] = newData[updatedEntityName]["_ref"]
		r = f(endpoint, updatedEntity)
		attempts += 1
	if (r.status_code == constants.UPDATE_CONFLICT):
		logger.getLogger().error("Attempted to update user. Request failed with reference error.")
		raise ValueError("Error attempting to update entity. Try again later.")
	return r

"""Receives a user represented by a json structure and attempts to update its data.
Returns False if the user id does not match any user id or _ref value is invalid.
Returns True if the user info was successfully updated."""
def updateUser(user_js):
	endpoint = USER_END + "/" + user_js["_id"] + QUERY_TOKEN
	r = _permformUpdate(lambda ep, u: requests.put(ep, json.dumps(u), headers=headers), endpoint, "user", user_js)
	if (r.status_code == constants.NOT_FOUND):
		return (False, r.json()['message'])
	if (r.status_code != constants.SUCCESS):
		raise Exception("Shared Server returned error: %d"%(r.status_code))
	return (True, r.json()['user'])

""" Asks shared server to create a new user"""
def createUser(user_js):
	#user_js["_ref"] = ""

	r = requests.post(USER_END + QUERY_TOKEN, data = json.dumps(user_js), headers=headers)

	if (r.status_code != constants.CREATE_SUCCESS):
		return (r.status_code, r.json())

	print("CREATED RESPONSE:" + str(r.json()))
	return (r.status_code, r.json()["user"])

"""Receives a user represented by a json structure and validates its credentials.
Returns True if the credentials were invalid, returns False otherwise.
"""
def validateUser(user_js):

	#userInfo = {"_username" : user_js['username'], "password" : user_js['password'], "facebookAuthToken" : user_js['fbToken'] }
	#return (True, userInfo)

	print(user_js)
	r = requests.post(USER_END + "/validate" + QUERY_TOKEN, data = json.dumps(user_js), headers=headers)
	if (r.status_code != constants.SUCCESS):
		logger.getLogger("Shared Server returned error: %d"%(r.status_code))
		return (False, r)
	return (True, r.json()['user'])

"""Receives a user id and attempts to delete it. Returns True if the user exists and is correctly deleted.
Returns False if the user id does not match any user id.
"""
def deleteUser(userId):
	r = requests.delete(USER_END + "/" + str(userId) + QUERY_TOKEN, headers=headers)

	if (r.status_code != constants.DELETE_SUCCESS):
		logger.getLogger("Shared Server returned error: %d"%(r.status_code))
		return (False, r.status_code)
	return (True, r.status_code)


