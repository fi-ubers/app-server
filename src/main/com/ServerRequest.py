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

SS_URI = "http://127.0.0.1:5000/api"
if not "SS_URL" in os.environ:
	os.environ["SS_URL"] = SS_URI

DEFAULT_APP_TOKEN = 'Sorry, there is no token'
if not "APP_TOKEN" in os.environ:
	os.environ["APP_TOKEN"] = DEFAULT_APP_TOKEN

CARS_END = "/cars"
USER_END = os.environ["SS_URL"] + "/users" 
QUERY_TOKEN = "?token=" + os.environ["APP_TOKEN"]

#CARS = "/cars"
#TRANSACT_ENDPOINT = "/transactions"
#TRIPS_ENDPOINT = "/trips"

headers = {'Content-Type' : 'application/json'}
MAX_ATTEMPTS = 10

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
	endpoint = USER_END + "/" + str(user_js["_id"]) + QUERY_TOKEN
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

	print(user_js)
	print(USER_END)
	r = requests.post(USER_END + "/validate" + QUERY_TOKEN, data = json.dumps(user_js), headers=headers)
	print(r)
	print(r.json())
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

"""Receives a user id and returns a list of all the cars owned by that user
"""
def getUserCars(userId):
	r = requests.get(USER_END + "/" + str(userId) + CARS_END)
	if (r.status_code != constants.SUCCESS):
		logger.getLogger("Shared Server returned error: %d"%(r.status_code))
		raise Exception("Shared Server returned error: %d"%(r.status_code))
	return r.json()["cars"]


""" Receives a user id, a car owner and a dictionary containing the properties of the car
with the following layout:
{
  'name': 'brandName',
  'value': 'plateNumber'
}
Attempts to create a new car with the information given. 
Returns a car object on successful creation.
"""
def createUserCar(userId, carId, owner, properties):
	car_js["id"] = str(carId)
	car_js["_ref"] = ""
	car_js["owner"] = str(owner)
	car_js["properties"] = str([properties])
	r = requests.post(os.environ["SS_URL"] + USER_END + "/" + str(userId) + CARS_END, data = json.dumps(car_js), headers=headers)
	if (r.status_code != constants.CREATE_SUCCESS):
		raise Exception("Shared Server returned error: %d"%(r.status_code))
#	print("CREATED RESPONSE:" + str(r.json()))
	return r.json()["car"]


"""Receives a user id and attempts to delete it. Returns True if the user exists and is correctly deleted.
Returns False if the user id does not match any user id.
"""
def deleteUserCar(userId, carId):
	r = requests.delete(os.environ["SS_URL"] + USER_END + "/" + str(userId) + CARS_END + "/" + str(carId))
	if (r.status_code == constants.NOT_FOUND):
		return (False, r.status_code)
	if (r.status_code != constants.DELETE_SUCCESS):
		logger.getLogger("Shared Server returned error: %d"%(r.status_code))
		raise Exception("Shared Server returned error: %d"%(r.status_code))
	return (True, r.status_code)

















