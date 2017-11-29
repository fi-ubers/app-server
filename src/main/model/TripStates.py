"""
These are the states a trip can be in.
Refer to this module when setting or comparing trip states.
"""
import datetime

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

def trip_to_shared(trip):
	new_trip = {}
	new_trip["driver"] = trip["driverId"]
	new_trip["passenger"] = trip["passengerId"]
	new_trip["start"] = location_to_shared(trip["directions"]["origin"])
	new_trip["end"] = location_to_shared(trip["directions"]["destination"])
	new_trip["route"] = {} 
	new_trip["distance"] = trip["directions"]["distance"]
	new_trip["totalTime"] = trip["directions"]["duration"]
	new_trip["waitTime"] = 10 
	new_trip["travelTime"] = new_trip["totalTime"]

	return new_trip

