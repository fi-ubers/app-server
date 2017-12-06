from src.main.model import User

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
"transactions": transacList1, "trips" : tripList1}

user2 = {"_id": 2, "online": False, "birthdate": "6-10-1996", "country": "Norway", "email": "juanpa@mail.jp", "images": ["No tengo imagen"], "name": "Pablo", "surname": "Fresia", "type": "passenger", "username": "juanpi",
"cars": carList2 ,"transactions":transacList2, "trips" : tripList2}

user3 = {"_id": 3,  "birthdate": "17-10-1993", "country": "Georgia", "email": "euge@euge.com", "images": [ "No tengo imagen"	], "name": "Euge", "surname": "Mariotti", "type": "driver", "username": "euge","cars":carList3, "transactions": transacList3, "trips" : tripList3, "rating":{"rate":0, "rateCount":0}}


user4 = {"_id": 10, "birthdate": "3-1-1997", "country": "Italy", "email": "corneliusf@gmail.com", "images": [ "No tengo imagen" ],"name": "Cornelius", "surname": "Fudge", "type": "passenger","username": "cornelius999", "cars": carList1, "transactions": transacList1, "trips" : tripList1, "coord":{"lat":"0", "lng":"0"}, "online":True}


user5 = {"_id": 11, "birthdate": "3-1-1997", "country": "England", "email": "sh@holmes.com", "images": [ "No tengo imagen" ],"name": "Sherlock", "surname": "Holmes", "type": "passenger","username": "sherlockholmes", "cars": carList1, "transactions": transacList1, "trips" : tripList1, "coord":{"lat":"0", "lng":"0"}, "online":True}

default_db = [user1, user2, user3, user4, user5]

class CollectionMock(object):
	def __init__(self, collection):
		self.docs = []
		self.source = []
		if collection == "online":
			for u in default_db[0:4]:
				self.source.append(User.UserJSON(u))

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

	def update(self, cond, params):
		for key in cond.keys():
			for doc in self.docs:
				if (doc.has_key(key) or doc[key] == cond[key]):
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


"""
class CollectionMock(object):
	def __init__(self, collection):
		print("Someone wants collection " + collection)
		if collection == "online":
			self.collection = UserCollectionMock(default_db)
		else:
			self.collection = TripsCollectionMock() 

	def update(self, cond, params):
		return self.collection.update(cond, params)

	def reset(self):
		return self.collection.reset()

	def find(self, match={}):
		return self.collection.find(match)

	def insert_one(self, new):
		return self.collection.insert_one(new)

	def delete_many(self, cond):
		return self.collection.delete_many(cond)
"""
