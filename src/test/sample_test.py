import json


default_db = [{
			"_id": 3,
			"birthdate": "17-10-1993",
			"country": "Georgia",
			"email": "euge@euge.com",
			"images": [
				"No tengo imagen"
				],
			"name": "Euge",
			"surname": "Mariotti",
			"type": "driver",
			"username": "euge"
		},
		{
			"_id": 1,
			"birthdate": "18-7-1994",
			"country": "Norway",
			"email": "juanma@mail.jm",
			"images": [
				"No tengo imagen"
				],
			"name": "Juan",
			"surname": "Fresia",
			"type": "passenger",
			"username": "juan"
		},
		{
			"_id": 2,
			"id" : 2,
			"birthdate": "6-10-1996",
			"country": "Norway",
			"email": "juanpa@mail.jp",
			"images": [
				"No tengo imagen"
				],
			"name": "Pablo",
			"surname": "Fresia",
			"type": "passenger",
			"username": "juanp"
		}]

MOCK_TOKEN = '?token=untokendementira'
MOCK_URL = 'http://172.17.0.2:80'

from src.main.com import ServerRequest, TokenGenerator

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

from mock import Mock, patch
from src.main.mongodb import MongoController
MongoController.getCollection = Mock(return_value = UserCollectionMock())


from src.main.resources import UserLogin
from src.main.myApp import application as app
from src.main.com import ServerRequest, TokenGenerator

ServerRequest.QUERY_TOKEN = MOCK_TOKEN

class FakeGet(object):
	def __init__(self, url, headers={}):
		print("El mock funcionaaa")
		self.url = url
		self.headers = headers
		self.data = default_db
		self.status_code = 0
		if (self.url == MOCK_URL + '/users/2' + MOCK_TOKEN):
			self.status_code = 200

	def json(self):
		if (self.url == MOCK_URL + '/users/2' + MOCK_TOKEN):
			print(self.url)
			return {'user' : self.data[2]}
		return {'message' : "Esto es un mensaje del mock"}



class TestUsersLogin(object):
	
	def test_getall_users_unauthorized(self):
		expected = "Bad request - missing token"
		self.app = app.test_client()
		response = self.app.get('/users')

		response_parsed = json.loads(response.get_data())
		assert (response_parsed["message"]== expected and response.status_code == 400)

	@patch('src.main.com.TokenGenerator.validateToken', return_value=(True, {"username" : "juanasda", "_id" : 1}))
	def test_getall_users_authorized(self, validateTokenMock):
		expected = default_db[0:2]

		self.app = app.test_client()
		response = self.app.get('/users', headers={"UserToken" : "A fake token"})

		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert (response_parsed['message']['users'] == expected and response.status_code == 200)


	@patch('src.main.com.TokenGenerator.validateToken', return_value=(True, {"username" : "juanasda", "_id" : 1}))
	def test_get_user_by_id_in_app(self, validateTokenMock):
		expected = default_db[0]

		self.app = app.test_client()
		response = self.app.get('/users/3', headers={"UserToken" : "A fake token"})

		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert (response_parsed['users'] == expected and response.status_code == 200)

	@patch('src.main.com.TokenGenerator.validateToken', return_value=(True, {"username" : "juanasda", "_id" : 1}))
	@patch('src.main.com.ServerRequest.requests.get', side_effect=FakeGet)
	def test_get_user_by_id_in_shared(self, validateTokenMock, FakeGet):
		expected = default_db[2]

		self.app = app.test_client()
		response = self.app.get('/users/2', headers={"UserToken" : "A fake token"})

		print(response)

		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert (response_parsed['users'] == expected and response.status_code == 200)




"""
	@patch('src.main.com.ServerRequest.requests.get', side_effect=FakeGet)
	def test_users(self, FakeGet):
		expected = { "users" : [ { "_id" : 1, "name" : "Juan" } ] }

		self.app = app.test_client()
		response = self.app.get('/users/199')

		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert (response_parsed == expected and response.status_code == 200)
"""

"""
	def test_insert_success(self):
		MongoController.getCollection().reset()
		new_user = { "id" : 2, "name" : "Ale" }
		expected = { "user" : { "_id" : 2, "name" : "Ale" } }

		self.app = app.test_client()
		response = self.app.post('/greet', data = json.dumps({ "user" : new_user }),
				content_type = 'application/json')

		response_parsed = json.loads(response.get_data())
		assert (response_parsed == expected and response.status_code == 201)


	def test_insert_duplicate(self):
		MongoController.getCollection().reset()
		new_user = [{ "id" : 1, "name" : "Ale" }]
		expected = { "message" : "user id already exists" }

		self.app = app.test_client()
		response = self.app.post('/greet', data = json.dumps({ "user" : new_user[0] }),
				content_type = 'application/json')

		response_parsed = json.loads(response.get_data())
		assert (response_parsed == expected and response.status_code == 400)


#	def test_get_nonexistent_user(self):
#		MongoController.getCollection().reset()
#		self.app = app.test_client()
#		response = self.app.get('/users/2')

#		assert (response.status_code == 404)


	def test_post_missing_id(self):
		MongoController.getCollection().reset()
		new_user = [{ "name" : "Ale" }]
		expected = { "message" : "request missing id" }

		self.app = app.test_client()
		response = self.app.post('/greet', data = json.dumps({ "user" : new_user[0] }),
				content_type = 'application/json')

		response_parsed = json.loads(response.get_data())
		assert (response_parsed == expected and response.status_code == 400)


#	def test_remove_success(self):
#		MongoController.getCollection().reset()
#		fake_users = [{ "_id" : 1, "name" : "Juan" }]
#		expected = { "user" : fake_users[0] }

#		self.app = app.test_client()
#		response = self.app.delete('/users/1')

#		response_parsed = json.loads(response.get_data())
#		assert (response_parsed == expected and response.status_code == 200)

#	def test_delete_invalid(self):
#		MongoController.getCollection().reset()
#		self.app = app.test_client()
#		response = self.app.delete('/users/2')
#		assert (response.status_code == 404)


