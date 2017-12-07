from src.main.model import User, TripStates

carList1 = [ {"_id":"12","_ref":"123", "owner":"FIUBER", "properties":[ {"name": "Ford", "value": "LDR123" } ] } ]
transacList1 = [{"id": "11111", "trip": "2", "timestamp": 0, "cost": {"currency": "galleon", "value": 100 },"description": "very expensive", "data": {} }]
tripList1 = [ { "id": "1", "applicationOwner": "FIUBER", "driver": "Dumbledore",  "passenger": "juan",  "start": { "address": { "street": "Av. Santa Fe", "location": { "lat": 0, "lon": 0 } },
"timestamp": 0 }, "end": { "address": { "street": "Av. Paseo Colon", "location": { "lat": 0, "lon": 0  }}, "timestamp": 0}, "totalTime": 0, "waitTime": 0, "travelTime": 0, "distance": 0,
"route": [{ "location": { "lat": 0, "lon": 0 }, "timestamp": 0 }], "cost": { "currency": "string", "value": 0 }}]

carList2 = [ { "_id":"14","_ref":"666", "owner":"FIUBER", "properties":[{"name": "Audi", "value": "LDR456"  }] } ]
transacList2= [{"id": "11111", "trip": "2", "timestamp": 0, "cost": { "currency": "galleon", "value": 5000 }, "description": "I have been robbed", "data": {} } ]
tripList2 = [{ "id": "2", "applicationOwner": "FIUBER", "driver": "Dumbledore",  "passenger": "juan",  "start": { "address": { "street": "Av. Las Heras", "location": { "lat": 0, "lon": 0 } },
"timestamp": 0 }, "end": { "address": { "street": "Av. Paseo Colon", "location": { "lat": 0, "lon": 0  }}, "timestamp": 0}, "totalTime": 0, "waitTime": 0, "travelTime": 0, "distance": 0,
"route": [{ "location": { "lat": 0, "lon": 0 }, "timestamp": 0 }], "cost": { "currency": "string", "value": 0 }}]

carList3 = [{"_id":"17","_ref":"555", "owner":"FIUBER", "properties":[{"name": "Mercedes", "value": "LDR789" }] } ]
transacList3 = []
tripList3 = []



user1 = {"_id": 1, "birthdate": "18-7-1994", "country": "Norway", "email": "juanma@mail.jm", "images": [ "No tengo imagen" ],"name": "Juan", "surname": "Fresia", "type": "passenger","username": "juan", "cars": carList1,
"transactions": transacList1, "trips" : tripList1, "online": True}
user2 = {"_id": 2, "online": False, "birthdate": "6-10-1996", "country": "Norway", "email": "juanpa@mail.jp", "images": ["No tengo imagen"], "name": "Pablo", "surname": "Fresia", "type": "passenger", "username": "juanpi",
"cars": carList2 ,"transactions":transacList2, "trips" : tripList2}
user3 = {"_id": 3,  "birthdate": "17-10-1993", "country": "Georgia", "email": "euge@euge.com", "images": [ "No tengo imagen"	], "name": "Euge", "surname": "Mariotti", "type": "driver", "username": "euge","cars":carList3, "transactions": transacList3, "trips" : tripList3, "rating":{"rate":0, "rateCount":0}, "online": False} 
user4 = {"_id": 10, "birthdate": "3-1-1997", "country": "Italy", "email": "corneliusf@gmail.com", "images": [ "No tengo imagen" ],"name": "Cornelius", "surname": "Fudge", "type": "driver","username": "cornelius999", "cars": carList1, "transactions": transacList1, "trips" : tripList1, "coord":{"lat":"0", "lng":"0"}, "online":True}



### These users have a special numbering scheme: 1xx is a passenger, 2xx is a driver. The last two digits represents realtive state (e.g. 0 == Idle, 1 == waiting_accept | waiting_confirm, etc)
user100 = {"_id" : 100, "username" : "user100", "online" : True, "type" : "passenger", "state" : User.USER_PSG_IDLE}
user101 = {"_id" : 101, "username" : "user101", "online" : True, "type" : "passenger", "state" : User.USER_PSG_WAITING_ACCEPT}
user102 = {"_id" : 102, "username" : "user102", "online" : True, "type" : "passenger", "state" : User.USER_PSG_SELECTING_DRIVER}
user103 = {"_id" : 103, "username" : "user103", "online" : True, "type" : "passenger", "state" : User.USER_PSG_SELECTING_DRIVER}
user104 = {"_id" : 104, "username" : "user104", "online" : True, "type" : "passenger", "state" : User.USER_PSG_WAITING_DRIVER}
user105 = {"_id" : 105, "username" : "user105", "online" : True, "type" : "passenger", "state" : User.USER_PSG_WAITING_DRIVER}
user106 = {"_id" : 106, "username" : "user106", "online" : True, "type" : "passenger", "state" : User.USER_PSG_WAITING_DRIVER}
user107 = {"_id" : 107, "username" : "user107", "online" : True, "type" : "passenger", "state" : User.USER_PSG_WAITING_START}
user108 = {"_id" : 108, "username" : "user108", "online" : True, "type" : "passenger", "state" : User.USER_PSG_TRAVELING}
user109 = {"_id" : 109, "username" : "user109", "online" : True, "type" : "passenger", "state" : User.USER_PSG_TRAVELING}
user110 = {"_id" : 110, "username" : "user110", "online" : True, "type" : "passenger", "state" : User.USER_PSG_TRAVELING}
user111 = {"_id" : 111, "username" : "user111", "online" : True, "type" : "passenger", "state" : User.USER_PSG_WAITING_FINISH}
user112 = {"_id" : 112, "username" : "user112", "online" : True, "type" : "passenger", "state" : User.USER_PSG_ARRIVED}
user113 = {"_id" : 113, "username" : "user113", "online" : True, "type" : "passenger", "state" : User.USER_PSG_ARRIVED}

user200 = {"_id" : 200, "username" : "user200", "online" : True, "type" : "driver", "state" : User.USER_DRV_IDLE}
user201 = {"_id" : 201, "username" : "user201", "online" : True, "type" : "driver", "state" : User.USER_DRV_WAITING_CONFIRMATION}
user202 = {"_id" : 202, "username" : "user202", "online" : True, "type" : "driver", "state" : User.USER_DRV_WAITING_CONFIRMATION}
user203 = {"_id" : 203, "username" : "user203", "online" : True, "type" : "driver", "state" : User.USER_DRV_GOING_TO_PICKUP}
user204 = {"_id" : 204, "username" : "user204", "online" : True, "type" : "driver", "state" : User.USER_DRV_WAITING_START}
user205 = {"_id" : 205, "username" : "user205", "online" : True, "type" : "driver", "state" : User.USER_DRV_GOING_TO_PICKUP}
user206 = {"_id" : 206, "username" : "user206", "online" : True, "type" : "driver", "state" : User.USER_DRV_GOING_TO_PICKUP}
user207 = {"_id" : 207, "username" : "user207", "online" : True, "type" : "driver", "state" : User.USER_DRV_TRAVELING}
user208 = {"_id" : 208, "username" : "user208", "online" : True, "type" : "driver", "state" : User.USER_DRV_WAITING_FINISH}
user209 = {"_id" : 209, "username" : "user209", "online" : True, "type" : "driver", "state" : User.USER_DRV_TRAVELING}
user210 = {"_id" : 210, "username" : "user210", "online" : True, "type" : "driver", "state" : User.USER_DRV_TRAVELING}

default_db = [user1, user2, user3, user4, user100, user101, user102, user103, user104, user105, user106, user107,
		user108, user109, user110, user111, user112, user113, user200, user201, user202, user203, user204, user205, user206,
		user207, user208, user209, user210 ]

trip1 = { "_id" : "1", "state" : TripStates.TRIP_PROPOSED }
trip2 = { "_id" : "2", "state" : TripStates.TRIP_PROPOSED, "passengerId" : user101["_id"] }
trip3 = { "_id" : "3", "state" : TripStates.TRIP_ACCEPTED, "passengerId" : user102["_id"], "driverId" : user201["_id"] }
trip4 = { "_id" : "4", "state" : TripStates.TRIP_ACCEPTED, "passengerId" : user103["_id"], "driverId" : user202["_id"] }
trip5 = { "_id" : "5", "state" : TripStates.TRIP_CONFIRMED, "passengerId" : user104["_id"], "driverId" : user203["_id"] }
trip6 = { "_id" : "6", "state" : TripStates.TRIP_STARTED_DRIVER, "passengerId" : user105["_id"], "driverId" : user204["_id"] }
trip7 = { "_id" : "7", "state" : TripStates.TRIP_CONFIRMED, "passengerId" : user106["_id"], "driverId" : user205["_id"] }
trip8 = { "_id" : "8", "state" : TripStates.TRIP_STARTED_PASSENGER, "passengerId" : user107["_id"], "driverId" : user206["_id"] }
trip9 = { "_id" : "9", "state" : TripStates.TRIP_STARTED, "passengerId" : user108["_id"], "driverId" : user207["_id"] }
trip10 = { "_id" : "10", "state" : TripStates.TRIP_FINISHED_DRIVER, "passengerId" : user109["_id"], "driverId" : user208["_id"] }
trip11 = { "_id" : "11", "state" : TripStates.TRIP_STARTED, "passengerId" : user110["_id"], "driverId" : user209["_id"] }
trip12 = { "_id" : "12", "state" : TripStates.TRIP_FINISHED_PASSENGER, "passengerId" : user111["_id"], "driverId" : user210["_id"] }
trip13 = { "_id" : "13", "state" : TripStates.TRIP_FINISHED, "passengerId" : user112["_id"], "driverId" : user210["_id"] }
trip14 = { "_id" : "14", "state" : TripStates.TRIP_FINISHED, "passengerId" : user113["_id"], "driverId" : user210["_id"],
		"directions" : { "origin" : {"lat" : 10, "lng" : 14}, "destination" : {"lat" : 11, "lng" : 15}, "distance" : 20, "duration" : 10, "path" : [], "status" : "OK" } }
trips_db = [ trip1, trip2, trip3, trip4, trip5, trip6, trip7, trip8, trip9, trip10, trip11, trip12, trip13, trip14 ]

class CollectionMock(object):
	def __init__(self, collection):
		self.docs = []
		self.source = []
		if collection == "online":
			for u in default_db:
				self.source.append(User.UserJSON(u))
		elif collection == "active_trips":
			for t in trips_db:
				self.source.append(t)
		self.reset()

	def reset(self):
		self.docs = []
		for d in self.source:
			self.docs.append(d)

	def find(self, match={}):
		if not "_id" in match:
			return self.docs
		for u in self.docs:
			if u["_id"] == match["_id"]:
				return [u]
		return [] 

	def insert_one(self, new):
		self.docs.append(new)

	def delete_many(self, cond):
		for key in cond.keys():
			for doc in self.docs:
				if (doc.has_key(key) or doc[key] == cond[key]):
					self.docs.remove(doc)

	def update_one(self, cond, params):
		return self.update(cond, params)

	def update(self, cond, params):
		for key in cond.keys():
			for doc in self.docs:
				if (doc.has_key(key) and doc[key] == cond[key]):
					if params.has_key('$push') and doc.has_key(params['$push'].keys()[0]):
						parameters = params['$push']
						listname = parameters.keys()[0]
						alist = doc[listname]
						alist.append(parameters[listname])
					if params.has_key('$pull') and doc.has_key(params['$pull'].keys()[0]):
						parameters = params['$pull']
						listname = parameters.keys()[0]
						filterName = parameters[listname].keys()[0]
						filterValue = parameters[listname][filterName]
						print("filter " + str(filterName) + " value " + str(filterValue)+ " list " + str(listname) )
						alist = doc[listname]
						for item in alist:
							if item[filterName] == filterValue:
								alist.remove(item)
					if params.has_key('$set'):
						parameters = params['$set']
						print(parameters)
						doc[parameters.keys()[0]] = parameters[parameters.keys()[0]]

	def remove(self, cond):
		pass
