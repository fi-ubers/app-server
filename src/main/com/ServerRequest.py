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

SS_URI = "http://127.0.0.1:5000/api" #'https://fiuber-shared-server.herokuapp.com/api'
if not "SS_URL" in os.environ:
	os.environ["SS_URL"] = SS_URI

DEFAULT_APP_TOKEN="Sorry there is no token"

if not "APP_TOKEN" in os.environ:
	os.environ["APP_TOKEN"] = DEFAULT_APP_TOKEN

QUERY_TOKEN = "?token=" + os.environ["APP_TOKEN"]

CARS_END = "/cars"
USER_END = os.environ["SS_URL"] + "/users"
TRANSACT_END = "/transactions"
TRIPS_END = "/trips"

headers = {'Content-Type' : 'application/json'}
MAX_ATTEMPTS = 10

"""Returns a list of all the users and their information in json format."""
def getUsers():
	r = requests.get(USER_END + QUERY_TOKEN, headers=headers)
	if (r.status_code != constants.SUCCESS):
		logger.getLogger("Shared Server returned error: %d"%(r.status_code))
		raise Exception("Shared Server returned error: %d"%(r.status_code))
	return (r.status_code, r.json()["users"])


"""Receives a user id. Returns the information of the user that matches that id in json format.
"""
def getUser(userId):
	r = requests.get(USER_END + "/" + str(userId) + QUERY_TOKEN, headers=headers)

	if (r.status_code != constants.SUCCESS):
		logger.getLogger("Shared Server returned error: %d"%(r.status_code))
		return (r.status_code, r.json())
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
	r = requests.post(USER_END + QUERY_TOKEN, data = json.dumps(user_js), headers=headers)

	if (r.status_code != constants.CREATE_SUCCESS):
		logger.getLogger("Shared Server returned error: %d"%(r.status_code))
		return (r.status_code, r.json())
	return (r.status_code, r.json()["user"])

"""Receives a user represented by a json structure and validates its credentials.
Returns True if the credentials were invalid, returns False otherwise.
"""
def validateUser(user_js):
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

"""Receives a user id and returns a list of all the cars owned by that user.
"""
def getUserCars(userId):
	r = requests.get(USER_END + "/" + str(userId) + CARS_END)
	if (r.status_code != constants.SUCCESS):
		logger.getLogger("Shared Server returned error: %d"%(r.status_code))
		raise Exception("Shared Server returned error: %d"%(r.status_code))
	return (r.status_code, r.json()["cars"])

"""Receives a user id and a car id. Returns the information of the car with
matching id that belongs to the identified user.
"""
def getUserCar(userId, carId):
	r = requests.get(USER_END + "/" + str(userId) + CARS_END + "/" + str(carId) + QUERY_TOKEN, headers=headers)
	if (r.status_code != constants.SUCCESS):
		logger.getLogger("Shared Server returned error: %d"%(r.status_code))
		return (r.status_code, r.json())
	return (r.status_code, r.json()["car"])

""" Receives a user id, a car owner and a dictionary containing the properties of the car
with the following layout:
{
  'name': 'brandName',
  'value': 'plateNumber'
}
Attempts to create a new car with the information given.
Returns a car object on successful creation.
"""
def createUserCar(userId, carProperties):
	carInfo = { "id" : "1" }
	carInfo["_ref"] = "1"
	carInfo["owner"] = "FIUBER"
	carInfo["properties"] =  [carProperties]
	r = requests.post(USER_END + "/" + str(userId) + CARS_END + QUERY_TOKEN, data = json.dumps(carInfo), headers=headers)
	if (r.status_code != constants.CREATE_SUCCESS):
		logger.getLogger("Shared Server returned error: %d"%(r.status_code))
		return (r.status_code, r.json())
	return (r.status_code, r.json()["car"])

"""Receives a user id and attempts to delete it. Returns True if the user exists and is correctly deleted.
Returns False if the user id does not match any user id.
"""
def deleteUserCar(userId, carId):
	r = requests.delete(USER_END + "/" + str(userId) + CARS_END + "/" + str(carId) + QUERY_TOKEN)
	if (r.status_code == constants.NOT_FOUND):
		return (False, r.status_code)
	if (r.status_code != constants.DELETE_SUCCESS):
		logger.getLogger("Shared Server returned error: %d"%(r.status_code))
		raise Exception("Shared Server returned error: %d"%(r.status_code))
	return (True, r.status_code)


"""Receives a user id number, a car id number and a car represented by a json structure with the following layout:
	{
	  "id": "string",
	  "_ref": "string",
	  "owner": "string",
	  "properties": [
	    {
	      "name": "string",
	      "value": "string"
	    }
	  ]
	}
Returns False if the user and car ids do not match any existing vehicles.
Returns True if the car info was successfully updated."""
def updateUserCar(userId, carId, car):
	endpoint = USER_END + "/" + str(userId) + CARS_END + "/" + str(carId) + QUERY_TOKEN
	r = _permformUpdate(lambda ep, u: requests.put(ep, json.dumps(u), headers=headers), endpoint, "car", car)
	if (r.status_code == constants.NOT_FOUND):
		return (False, r.json()['message'])
	if (r.status_code != constants.SUCCESS):
		logger.getLogger("Shared Server returned error: %d"%(r.status_code))
		return (r.status_code, r.json())
	return (True, r.json()['car'])


"""Receives a user id and returns a list with all the transactions made by that user.
"""
def getUserTransactions(id):
	endpoint = USER_END + "/" + str(id) + TRANSACT_END + QUERY_TOKEN
	r = requests.get(endpoint, headers=headers)
	if (r.status_code != constants.SUCCESS):
		logger.getLogger("Shared Server returned error: %d"%(r.status_code))
		return (r.status_code, r.json())
	return (r.status_code, r.json()['transactions'])


"""Receives a user id and a json representing a transaction with the following layout:
	  {
	    "trip": "string",
	    "timestamp": 0,
	    "cost": {
	      "currency": "string",
	      "value": 0
	    },
	    "description": "string",
	    "data": {}
	  }
Returns a tuple (True, transaction) if the transaction was successfully created.
"""
def makePayment(id, transaction):
	endpoint = USER_END + "/" + str(id) + TRANSACT_END + QUERY_TOKEN
	transaction["id"] = "1"
	r = requests.put(endpoint, data = json.dumps(transaction), headers=headers)
	if (r.status_code != constants.SUCCESS):
		logger.getLogger("Shared Server returned error: %d"%(r.status_code))
		return (r.status_code, r.json())
	return (r.status_code, r.json()["transaction"])

"""Receives a user id. Returns a json structures with the following layout:
  "trips": [
    {
      "id": "string",
      "applicationOwner": "owner name",
      "driver": "driver id",
      "passenger": "passanger id",
      "start": {
        "address": {
          "street": "street name",
          "location": {
            "lat": 0,
            "lon": 0
          }
        },
        "timestamp": 0
      },
      "end": {
        "address": {
          "street": "street name",
          "location": {
            "lat": 0,
            "lon": 0
          }
        },
        "timestamp": 0
      },
      "totalTime": 0,
      "waitTime": 0,
      "travelTime": 0,
      "distance": 0,
      "route": [
        {
          "location": {
            "lat": 0,
            "lon": 0
          },
          "timestamp": 0
        }
      ],
      "cost": {
        "currency": "coin",
        "value": 0
      }
    }
  ]
"""
def getUserTrips(id):
	endpoint = USER_END + "/" + str(id) + TRIPS_END + QUERY_TOKEN
	r = requests.get(endpoint, headers=headers)
	if (r.status_code != constants.SUCCESS):
		logger.getLogger("Shared Server returned error: %d"%(r.status_code))
		return (r.status_code, r.json())
	return (r.status_code, r.json()['trips'])

"""Receives a json structure representing a trip, with the following layout:
  "trip": {
    "id": "string",
    "applicationOwner": "string",
    "driver": "string",
    "passenger": "string",
    "start": {
      "address": {
        "street": "string",
        "location": {
          "lat": 0,
          "lon": 0
        }
      },
      "timestamp": 0
    },
    "end": {
      "address": {
        "street": "string",
        "location": {
          "lat": 0,
          "lon": 0
        }
      },
      "timestamp": 0
    },
    "totalTime": 0,
    "waitTime": 0,
    "travelTime": 0,
    "distance": 0,
    "route": [
      {
        "location": {
          "lat": 0,
          "lon": 0
        },
        "timestamp": 0
      }
    ],
    "cost": {
      "currency": "string",
      "value": 0
    }
  },
  "paymethod": {
    "paymethod": "string",
    "parameters": {}
  }

Returns a tuple (201, trip) if the trip was successfully created.
"""
def createTrip(trip):
	r = requests.post(os.environ["SS_URL"] + TRIPS_END + QUERY_TOKEN, data = json.dumps(trip), headers=headers)
	if (r.status_code != constants.CREATE_SUCCESS):
		logger.getLogger("Shared Server returned error: %d"%(r.status_code))
		return (r.status_code, r.json())
	return (r.status_code, r.json()["trip"])
