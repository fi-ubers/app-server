"""
These are the states a trip can be in.
Refer to this module when setting or comparing trip states.
"""
import datetime
from dateutil import parser as dtparser
from src.main.mongodb import MongoController
from src.main.com import Distances
import logging as logger

TRIP_PROPOSED = "proposed"
TRIP_ACCEPTED = "accepted"
TRIP_CONFIRMED = "confirmed"
TRIP_STARTED_PASSENGER = "started_passenger"
TRIP_STARTED_DRIVER = "started_driver"
TRIP_STARTED = "started"
TRIP_FINISHED_PASSENGER ="finished_passenger"
TRIP_FINISHED_DRIVER = "finished_driver"
TRIP_FINISHED = "finished"
TRIP_FINISHED_RATED = "finished_rated"
TRIP_PAYED = "payed"

TRIP_START_VALID = [TRIP_CONFIRMED, TRIP_STARTED_PASSENGER, TRIP_STARTED_DRIVER]
TRIP_FINISH_VALID = [TRIP_STARTED, TRIP_FINISHED_PASSENGER, TRIP_FINISHED_DRIVER]
TRIP_ABLE_TO_PAY = [TRIP_FINISHED, TRIP_FINISHED_RATED]
TRIP_CANCELABLE = [TRIP_PROPOSED, TRIP_ACCEPTED, TRIP_CONFIRMED, TRIP_STARTED_PASSENGER, TRIP_STARTED_DRIVER]

ACTION_CANCEL = "cancel"
ACTION_DRIVER_ACCEPT = "accept"
ACTION_PASSENGER_CONFIRM = "confirm"
ACTION_PASSENGER_REJECT = "reject"
ACTION_START = "start"
ACTION_FINISH = "finish"
ACTION_RATE = "rate"
ACTION_PAY = "pay"


def location_to_shared(loc):
	new_loc = {}
	new_loc["address"] = {}
	new_loc["address"]["location"] = {}
	new_loc["address"]["location"]["lat"] = loc["lat"]
	new_loc["address"]["location"]["lon"] = loc["lng"]
	new_loc["timestamp"] = loc["timestamp"] if "timestamp" in loc else datetime.datetime.now().isoformat()
	return new_loc

def route_to_shaerd(route):
	route_sh = []
	for wp in route:
		route_sh.append(location_to_shared(wp))	
	return route_sh

def timestamp_delta(ts1, ts2):
	dt1 = dtparser.parse(ts1)
	dt2 = dtparser.parse(ts2)
	return (dt2-dt1).total_seconds()

def trip_to_shared(trip):
	new_trip = {}
	new_trip["driver"] = trip["driverId"]
	new_trip["passenger"] = trip["passengerId"]
	new_trip["start"] = location_to_shared(trip["directions"]["origin"])
	new_trip["route"] = route_to_shaerd(trip["real_route"]) if "real_route" in trip else [] 
	new_trip["distance"] = trip["directions"]["distance"]
	new_trip["end"] = location_to_shared(trip["directions"]["destination"])
	new_trip["totalTime"] = trip["directions"]["duration"]
	new_trip["waitTime"] = 1
	new_trip["travelTime"] = new_trip["totalTime"]

	if len(new_trip["route"]) > 0:
		new_trip["end"] = new_trip["route"][-1]
		new_trip["travelTime"] = int(timestamp_delta(trip["time_start"], trip["time_finish"]))
		new_trip["waitTime"] = int(timestamp_delta(trip["time_start_waiting"], trip["time_start"]) + 1)
		new_trip["totalTime"] = new_trip["waitTime"] + new_trip["travelTime"]
		new_trip["distance"] = int(Distances.computeDistance(trip["directions"]["origin"], trip["directions"]["destination"]))


	if new_trip["waitTime"] <= 0:
		new_trip["waitTime"] = 1
	new_trip["cost"] = trip["cost"] if "cost" in trip else {}
	new_trip.pop("cost") 

	print(new_trip)
	return new_trip



def updateDriverLocation(tripId, user):
	active_trips = MongoController.getCollection("active_trips")
	trip = list(active_trips.find({"_id" : tripId}))
	if len(trip) <= 0:
		return
	trip = trip[0]

	if not trip["state"] == TRIP_STARTED:
		return

	if not trip["driverId"] == user["_id"]:
		return

	logger.getLogger().debug("Pushing new coordinates to trip (id: " + trip["_id"] + ")")
	# Now we know the trip is started, and we are the driver
	location = { "lat" : user["coord"]["lat"], "lng" : user["coord"]["lng"] }
	location["timestamp"] = datetime.datetime.now().isoformat()
	active_trips.update( { "_id" : tripId }, { "$push" : { "real_route" : location } } )





