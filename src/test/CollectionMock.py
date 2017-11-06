
carList1 = [ {"id":"12","_ref":"123", "owner":"FIUBER", "properties":[ {"name": "Ford", "value": "LDR123" } ] } ]
transacList1 = [{"id": "11111", "trip": "2", "timestamp": 0, "cost": {"currency": "galleon", "value": 100 },"description": "very expensive", "data": {} }]

carList2 = [ { "id":"14","_ref":"666", "owner":"FIUBER", "properties":[{"name": "Audi", "value": "LDR456"  }] } ]
transacList2= [{"id": "11111", "trip": "2", "timestamp": 0, "cost": { "currency": "galleon", "value": 5000 }, "description": "I have been robbed", "data": {} } ]

carList3 = [{"id":"17","_ref":"555", "owner":"FIUBER", "properties":[{"name": "Mercedes", "value": "LDR789" }] } ]
transacList3 = []

user1 = {"_id": 1, "birthdate": "18-7-1994", "country": "Norway", "email": "juanma@mail.jm", "images": [ "No tengo imagen" ],"name": "Juan", "surname": "Fresia", "type": "passenger","username": "juan", "cars": carList1,
"transactions": transacList1}

user2 = {"_id": 2, "id": 2, "birthdate": "6-10-1996", "country": "Norway", "email": "juanpa@mail.jp", "images": ["No tengo imagen"], "name": "Pablo", "surname": "Fresia", "type": "passenger", "username": "juanpi",
"cars": carList2 ,"transactions":transacList2 }

user3 = {"_id": 3, "id" : 3,  "birthdate": "17-10-1993", "country": "Georgia", "email": "euge@euge.com", "images": [ "No tengo imagen"	], "name": "Euge", "surname": "Mariotti", "type": "driver", "username": "euge",
"cars":carList3, "transactions": transacList3 }

default_db = [user1, user2, user3]

class UserCollectionMock(object):
	def __init__(self):
		self.users = default_db[0:2]

	def reset(self):
		self.users = default_db[0:2]

	def find(self):
		return self.users

	def insert_one(self, new):
		self.users.append(new)

	def delete_many(self, cond):
		for key in cond.keys():
			for user in self.users:
				if (user.has_key(key) or user[key] == cond[key]):
					self.users.remove(user)
