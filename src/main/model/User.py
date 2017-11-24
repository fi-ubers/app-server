def UserJSON(user_js):
	user_js["_id"] = user_js.pop("id") if user_js.has_key("id") else user_js.pop("_id")
	user_js["online"] = False if not user_js.has_key("online") else user_js["online"]
	user_js["coord"] = {"lat": "0", "lng": "0"} if not user_js.has_key("coord") else user_js["coord"]
	return user_js


def LocUserJSON(user_js):
	location_js = {}
	location_js["_id"] = user_js["_id"]
	location_js["online"] = user_js["online"]
	location_js["coord"] = user_js["coord"]
	return location_js

