USER_INVALID = 0
USER_IDLE = 1

USER_PSG_WAITING_ACCEPT = 2
USER_PSG_SELECTING_DRIVER = 3
USER_PSG_WAITING_DRIVER = 4
USER_TRAVELING = 5
USER_ARRIVED = 6

USER_WAITING_START = 7

USER_DRV_WAITING_CONFIRMATION = 12
USER_DRV_GOING_TO_PICKUP = 13

USER_TYPE_PASSENGER = "passenger"
USER_TYPE_DRIVER = "driver"

def UserJSON(user_js):
	user_js["_id"] = user_js.pop("id") if user_js.has_key("id") else user_js.pop("_id")
	user_js["online"] = False if not user_js.has_key("online") else user_js["online"]
	user_js["coord"] = {"lat": "0", "lng": "0"} if not user_js.has_key("coord") else user_js["coord"]
	user_js["state"] = USER_IDLE if not "state" in user_js else user_js["state"]
	return user_js


def LocUserJSON(user_js):
	location_js = {}
	location_js["_id"] = user_js["_id"]
	location_js["online"] = user_js["online"]
	location_js["coord"] = user_js["coord"]
	return location_js

