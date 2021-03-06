from src.main.com import Distances


USER_INVALID = 0

USER_PSG_IDLE = 1
USER_PSG_WAITING_ACCEPT = 2
USER_PSG_SELECTING_DRIVER = 3
USER_PSG_WAITING_DRIVER = 4
USER_PSG_WAITING_START = 7
USER_PSG_TRAVELING = 5
USER_PSG_ARRIVED = 6 
USER_PSG_WAITING_FINISH = 8


USER_DRV_IDLE = 11
USER_DRV_WAITING_CONFIRMATION = 12
USER_DRV_GOING_TO_PICKUP = 13
USER_DRV_WAITING_START = 15
USER_DRV_TRAVELING = 14
USER_DRV_WAITING_FINISH = 16

USER_TYPE_PASSENGER = "passenger"
USER_TYPE_DRIVER = "driver"

def UserJSON(user_js):
	user_js["_id"] = user_js.pop("id") if user_js.has_key("id") else user_js.pop("_id")
	user_js["online"] = False if not user_js.has_key("online") else user_js["online"]
	user_js["coord"] = {"lat": "0", "lng": "0"} if not user_js.has_key("coord") else user_js["coord"]

	user_state = USER_PSG_IDLE
	if(user_js["type"] == USER_TYPE_DRIVER):
		user_js["rating"] = {"rate":0, "rateCount":0} if not user_js.has_key("rating") else user_js["rating"] 
		user_state = USER_DRV_IDLE
		
	user_js["state"] = user_state if not "state" in user_js else user_js["state"]
	user_js["tripId"] = "" if not "tripId" in user_js else user_js["tripId"]

	user_js["balance"] = "Hello" if not "balance" in user_js else user_js["balance"]
	return user_js

def UserUpdateDedicatedFields(user_new, user_old):
	user_new["_id"] = user_old["_id"]
	user_new["online"] = user_old["online"]
	user_new["coord"] = user_old["coord"]
	user_new["state"] = user_old["state"]
	if user_new["type"] == USER_TYPE_DRIVER:
		user_new["rating"] = user_old["rating"]
	user_new["tripId"] = user_old["tripId"]
	return user_new


def LocUserJSON(user_js):
	location_js = {}
	location_js["_id"] = user_js["_id"]
	location_js["online"] = user_js["online"]
	location_js["coord"] = user_js["coord"]
	return location_js

def RatingUserJSON(user_js):
	rating_js = {}
	rating_js["_id"] = user_js["_id"]
	rating_js["rating"] = user_js["rating"]
	return rating_js

def distaceBetween(user1, user2):
	return Distances.computeDistance(user1["coord"], user2["coord"])
