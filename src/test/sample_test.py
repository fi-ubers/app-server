import json
import os

user1 = {"_id": 1, "birthdate": "18-7-1994", "country": "Norway",
		 "email": "juanma@mail.jm", "images": [ "No tengo imagen" ],
		 "name": "Juan", "surname": "Fresia", "type": "passenger",
		 "username": "juan" }

user2 = {"_id": 2, "id": 2, "birthdate": "6-10-1996", "country": "Norway",
		 "email": "juanpa@mail.jp", "images": ["No tengo imagen"],
		 "name": "Pablo", "surname": "Fresia", "type": "passenger",
		 "username": "juanpi"}

user3 = {"_id": 3, "id" : 3,  "birthdate": "17-10-1993", "country": "Georgia",
		 "email": "euge@euge.com", "images": [ "No tengo imagen"	],
		 "name": "Euge",	"surname": "Mariotti", "type": "driver",
		 "username": "euge" }

default_db = [user1, user2, user3]

MOCK_URL = 'http://172.17.0.2:80'
MOCK_TOKEN = '?token=untokendementira'
MOCK_TOKEN_VALIDATION = (True, {"username" : "juan", "_id" : 1})

os.environ['SS_URL'] = MOCK_URL

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


from src.main.com import ServerRequest, TokenGenerator
from src.main.resources import UserLogin
from src.main.myApp import application as app

ServerRequest.QUERY_TOKEN = MOCK_TOKEN

class FakeGet(object):
	def __init__(self, url, headers={}):
		self.url = url
		self.headers = headers
		self.db = default_db
		self.status_code = 0

		if (self.url == MOCK_URL + '/users/3' + MOCK_TOKEN):
			self.status_code = 200
			self.response = {'code' : self.status_code, 'user' : self.db[2] }
		elif (self.url == MOCK_URL + '/users/7' + MOCK_TOKEN):
			self.status_code = 404 
			self.response = {"code" : 404, 'message' : 'Not found'}
		else:
			self.response = {"code" : 666, 'message' : 'Mocking error'}

	def json(self):
		return self.response


class FakePost(object):
	def __init__(self, url, headers={}, data=''):
		self.url = url
		self.db = default_db
		self.data = data
		self.status_code = 0

		if (self.url == MOCK_URL + '/users' + MOCK_TOKEN):
			ret = json.loads(self.data)
			ret['id'] = 6
			ret.pop('password')
			self.status_code = 201
			self.response = { "code" : self.status_code, "user" : ret }
		else:
			self.response = {"code" : 666, 'message' : 'Mocking error'}

	def json(self):
		return self.response




class TestUsersLogin(object):
	
	def test_getall_users_unauthorized(self):
		expected = "Bad request - missing token"
		self.app = app.test_client()
		response = self.app.get('/users')

		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 400)
		assert(response_parsed["message"] == expected)
		assert(response_parsed["code"] == 400)

	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION)
	def test_getall_users_authorized(self, validateTokenMock):
		expected = default_db[0:2]

		self.app = app.test_client()
		response = self.app.get('/users', headers={"UserToken" : "A fake token"})

		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 200)
		assert(response_parsed['users'] == expected)
		assert(response_parsed['code'] == 200)


	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION)
	def test_get_user_by_id_in_app(self, validateTokenMock):
		expected = default_db[0]

		self.app = app.test_client()
		response = self.app.get('/users/1', headers={"UserToken" : "A fake token"})

		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 200)
		assert(response_parsed['user'] == expected)
		assert(response_parsed['code'] == 200)


	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION)
	@patch('src.main.com.ServerRequest.requests.get', side_effect=FakeGet)
	def test_get_user_by_id_in_shared(self, validateTokenMock, FakeGet):
		expected = default_db[2]

		self.app = app.test_client()
		response = self.app.get('/users/3', headers={"UserToken" : "A fake token"})

		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 200)
		assert(response_parsed['user'] == expected)
		assert(response_parsed['code'] == 200)

	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION)
	@patch('src.main.com.ServerRequest.requests.get', side_effect=FakeGet)
	def test_get_user_by_id_non_existent(self, validateTokenMock, FakeGet):
		self.app = app.test_client()
		response = self.app.get('/users/7', headers={"UserToken" : "A fake token"})

		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 404)
		assert(response_parsed['code'] == 404)

	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION)
	@patch('src.main.com.ServerRequest.requests.post', side_effect=FakePost)
	def test_register_new_user(self, validateTokenMock, FakeGet):
		expected = {"birthdate": "11-11-2011", "country": "Chile", "email": "fakemail@gmail.com", "password" : "hola9876",
					"images": ["No tengo imagen"], "name": "Cosme", "surname": "Fulanito", "type": "passenger", "username": "cosme_fulanito" }

		self.app = app.test_client()
		response = self.app.post('/users', headers={"UserToken" : "A fake token"}, data = json.dumps(expected), content_type='application/json')

		print(response)

		expected["_id"] = 6
		expected.pop("password")

		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 201)
		assert(response_parsed['user'] == expected)
		assert(response_parsed['code'] == 201)

"""
Some tests to add in the future:
	def test_insert_success(self):
	def test_insert_duplicate(self):
	def test_post_missing_id(self):
	def test_remove_success(self):
	def test_delete_invalid(self):
"""
