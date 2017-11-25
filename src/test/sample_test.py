import json
import os
import jwt
import random

V1_URL = '/v1/api'
MOCK_URL = 'http://172.17.0.2:80'
MOCK_TOKEN = '?token='
MOCK_TOKEN_VALIDATION_1 = (True, {"username" : "juan", "_id" : 1})
MOCK_TOKEN_VALIDATION_2 = (True, {"username" : "juanpi", "_id" : 2})
MOCK_TOKEN_VALIDATION_3 = (True, {"username" : "euge", "_id" : 3})
MOCK_TOKEN_VALIDATION_7 = (True, {"username" : "luis", "_id" : 7})
MOCK_TOKEN_VALIDATION_10 = (True, {"username" : "cornelius999", "_id" : 10})
MOCK_TOKEN_VALIDATION_11 = (True, {"username" : "sherlockholmes", "_id" : 11})

os.environ['SS_URL'] = MOCK_URL
os.environ["APP_TOKEN"] = "untokendementira"

from mock import Mock, patch
from CollectionMock import UserCollectionMock, default_db
from src.main.mongodb import MongoController
MongoController.getCollection = Mock(return_value = UserCollectionMock())

from src.main.com import ServerRequest, TokenGenerator
from src.main.resources import UserLogin
from src.main.myApp import application as app

ServerRequest.QUERY_TOKEN = MOCK_TOKEN

"""
This mock classes are to override ServerRequest.request methods.
With the @patch decorator it is posible to make request.get() return
the next fake object; so it can perform an url check and mutate
to simulate different endpoints on the shared server.
"""
class FakeGet(object):
	def __init__(self, url, headers={}):
		self.url = url
		self.headers = headers
		self.db = default_db
		self.status_code = 0
		
		if (self.url == MOCK_URL + '/users/3' + MOCK_TOKEN + os.environ["APP_TOKEN"]):
			self.status_code = 200
			self.response = {'code' : self.status_code, 'user' : self.db[2] }
		elif (self.url == MOCK_URL + '/users/7' + MOCK_TOKEN + os.environ["APP_TOKEN"]):
			self.status_code = 404 
			self.response = {"code" : 404, 'message' : 'Not found'}
		elif (self.url == MOCK_URL + '/users/10'+MOCK_TOKEN + os.environ["APP_TOKEN"]):
			self.status_code = 200
			self.response = {'code' : self.status_code, 'user' : self.db[3] }
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
		if (self.url == MOCK_URL + '/users' + MOCK_TOKEN + os.environ["APP_TOKEN"]):
			ret = json.loads(self.data)
			ret['id'] = 6
			if ret["email"] == "fakemail@error.com":
				self.status_code = 500
				self.response = {"code" : self.status_code, 'message' : 'Unknown Error'}				
			else:
				ret.pop('password')
				self.status_code = 201
				self.response = { "code" : self.status_code, "user" : ret }
		elif (self.url == MOCK_URL + '/users/validate' + MOCK_TOKEN + os.environ["APP_TOKEN"]):
			ret = json.loads(self.data)
			if ret["email"] == "fakemail@error.com":
				self.status_code = 400
				self.response = {"code" : self.status_code, 'message' : 'Unknown Error'}				
			else:
				self.status_code = 200
				self.response = { "code" : self.status_code, "user" : ret, "token" : os.environ["APP_TOKEN"] }	
		else:
			self.response = {"code" : 666, 'message' : 'Mocking error'}

	def json(self):
		return self.response


class FakePut(object):
	def __init__(self, url, headers={}, data=''):
		self.url = url
		self.db = default_db
		self.data = data
		self.status_code = 0

		if (self.url == MOCK_URL + '/users/1' + MOCK_TOKEN + os.environ["APP_TOKEN"]):
			ret = json.loads(self.data)
			ret['id'] = 1
			self.status_code = 200
			self.response = { "code" : self.status_code, "user" : ret }
		else:
			self.response = {"code" : 666, 'message' : 'Mocking error'}

	def json(self):
		return self.response


class FakeDelete(object):
	def __init__(self, url, headers={}):
		self.url = url
		self.db = default_db
		self.headers = headers
		self.status_code = 0

		if (self.url == MOCK_URL + '/users/1' + MOCK_TOKEN + os.environ["APP_TOKEN"]):
			self.status_code = 204
			self.response = { "code" : self.status_code, 'message' : 'delete successful'}
		if (self.url == MOCK_URL + '/users/2' + MOCK_TOKEN + os.environ["APP_TOKEN"]):
			self.status_code = 404
			self.response = { "code" : self.status_code, 'message' : 'non-existent id'}
		else:
			self.response = {"code" : 666, 'message' : 'Mocking error'}

	def json(self):
		return self.response

class TestUsersLogin(object):
	
	def test_getall_users_unauthorized(self):
		expected = "Bad request - missing token"
		self.app = app.test_client()
		response = self.app.get(V1_URL + '/users')

		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 400)
		assert(response_parsed["message"] == expected)
		assert(response_parsed["code"] == 400)

	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_1)
	def test_getall_users_authorized(self, validateTokenMock):
		expected = default_db[0:4]

		self.app = app.test_client()
		response = self.app.get(V1_URL + '/users', headers={"UserToken" : "A fake token"})

		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 200)
		assert(response_parsed['users'] == expected)
		assert(response_parsed['code'] == 200)


	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_1)
	def test_get_user_by_id_in_app(self, validateTokenMock):
		expected = default_db[0]
		expected["coord"] = {'lat': '0', 'lng': '0'}
		expected["online"] = False

		self.app = app.test_client()
		response = self.app.get(V1_URL + '/users/1', headers={"UserToken" : "A fake token"})

		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 200)
		assert(response_parsed['user'] == expected)
		assert(response_parsed['code'] == 200)


	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_3)
	@patch('src.main.com.ServerRequest.requests.get', side_effect=FakeGet)
	def test_get_user_by_id_in_shared(self, validateTokenMock, FakeGet):
		expected = default_db[2]

		self.app = app.test_client()

		response = self.app.get(V1_URL + '/users/3', headers={"UserToken" : "A fake token"})

		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 200)
		assert(response_parsed['user'] == expected)
		assert(response_parsed['code'] == 200)

	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_7)
	@patch('src.main.com.ServerRequest.requests.get', side_effect=FakeGet)
	def test_get_user_by_id_non_existent(self, validateTokenMock, FakeGet):
		self.app = app.test_client()
		response = self.app.get(V1_URL + '/users/7', headers={"UserToken" : "A fake token"})

		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 404)
		assert(response_parsed['code'] == 404)

	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_1)
	@patch('src.main.com.ServerRequest.requests.post', side_effect=FakePost)
	def test_register_new_user(self, validateTokenMock, FakeGet):
		expected = {"birthdate": "11-11-2011", "country": "Chile", "email": "fakemail@success.com", "password" : "hola9876", "state":"idle",
		"images": ["No tengo imagen"], "name": "Cosme", "surname": "Fulanito", "type": "passenger", "username": "cosme_fulanito" }

		self.app = app.test_client()
		response = self.app.post(V1_URL + '/users', headers={"UserToken" : "A fake token"}, data = json.dumps(expected), content_type='application/json')

		print(response)

		expected["_id"] = 6
		expected["coord"] = {'lat': '0', 'lng': '0'}
		expected["online"] = False
		expected.pop("password")

		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 201)
		assert(response_parsed['user'] == expected)
		assert(response_parsed['code'] == 201)

	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_1)
	@patch('src.main.com.ServerRequest.requests.post', side_effect=FakePost)
	def test_register_new_user_fail(self, validateTokenMock, FakeGet):
		expected = {"birthdate": "11-11-2011", "country": "Chile", "email": "fakemail@error.com", "password" : "hola9876",
		"images": ["No tengo imagen"], "name": "Cosme", "surname": "Fulanito", "type": "passenger", "username": "cosme_fulanito" }

		self.app = app.test_client()
		response = self.app.post(V1_URL + '/users', headers={"UserToken" : "A fake token"}, data = json.dumps(expected), content_type='application/json')

		print(response)

		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 500)
		assert(response_parsed['code'] == 500)


#	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_1)
#	@patch('src.main.com.ServerRequest.requests.put', side_effect=FakePut)
#	def test_modify_user_success(self, validateTokenMock, FakePut):
#		expected = {"_id":1, "_ref": 123, "birthdate": "18-7-1994", "country": "Russia", "email": "juanma@mail.jm", "images": [ "No tengo imagen" ], "name": "Juan", "surname": "Fresia", "type": "passenger", "username": "juan" }

#		self.app = app.test_client()
#		response = self.app.put(V1_URL + '/users/1', headers={'UserToken' : "A fake token"}, data = json.dumps(expected), content_type='application/json')
		
#		expected["id"] = 1

#		response_parsed = json.loads(response.get_data())
#		print(response_parsed)
#		assert(response.status_code == 200)
#		assert(response_parsed['user'] == expected)
#		assert(response_parsed['code'] == 200)


	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_1)
	@patch('src.main.com.ServerRequest.requests.delete', side_effect=FakeDelete)
	def test_delete_user_by_id_success(self, validateTokenMock, FakeDelete):
		self.app = app.test_client()
		response = self.app.delete(V1_URL + '/users/1', headers={'UserToken' : "A fake token"}, content_type='application/json')
		assert(response.status_code == 204)

	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_1)
	@patch('src.main.com.ServerRequest.requests.delete', side_effect=FakeDelete)
	def test_delete_user_by_id_forbidden(self, validateTokenMock, FakeDelete):
		self.app = app.test_client()
		response = self.app.delete(V1_URL + '/users/9', headers={'UserToken' : "A fake token"}, content_type='application/json')
		assert(response.status_code == 403)

	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_2)
	@patch('src.main.com.ServerRequest.requests.delete', side_effect=FakeDelete)
	def test_delete_user_by_id_nonexistent(self, validateTokenMock, FakeDelete):
		self.app = app.test_client()
		response = self.app.delete(V1_URL + '/users/2', headers={'UserToken' : "A fake token"}, content_type='application/json')
		assert(response.status_code == 404)


	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_1)
	@patch('src.main.com.ServerRequest.requests.post', side_effect=FakePost)
	def test_validate_user_error(self, validateTokenMock, FakePost):
		expected = {"birthdate": "11-11-2011", "country": "Chile", "email": "fakemail@error.com", "password" : "hola9876",
		"images": ["No tengo imagen"], "name": "Cosme", "surname": "Fulanito", "type": "passenger", "username": "cosme_fulanito", 'coord': {'lat': '0', 'lng': '0'} }

		self.app = app.test_client()
		response = self.app.post(V1_URL + '/users/login', headers={'UserToken' : "A fake token"}, data = json.dumps(expected), content_type='application/json')
		assert(response.status_code == 400)

	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_1)
	@patch('src.main.com.ServerRequest.requests.post', side_effect=FakePost)
	def test_validate_user_success(self, validateTokenMock, FakePost):
		expected = {"id":20, "birthdate": "11-11-2011", "country": "Chile", "email": "fakemail@success.com", "password" : "hola9876", "state":"idle",
		"images": ["No tengo imagen"], "name": "Cosme", "surname": "Fulanito", "type": "passenger", "username": "cosme_fulanito" }

		self.app = app.test_client()
		response = self.app.post(V1_URL + '/users/login', headers={"UserToken" : "A fake token"}, data = json.dumps(expected), content_type='application/json')
		response_parsed = json.loads(response.get_data())
		expected["_id"] = expected.pop("id")
		expected['coord']= {'lat': '0', 'lng': '0'}
		expected['online'] = True
		assert(response.status_code == 200)
		assert(response_parsed['user'] == expected)

	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_10)
	@patch('src.main.com.ServerRequest.requests.get', side_effect=FakeGet)
	def test_get_userlocation_success(self, validateTokenMock, FakeGet):
		expected = {}
		expected["_id"] = 10
		expected["online"] = True
		expected["coord"]= {'lat': '0', 'lng': '0'}

		self.app = app.test_client()
		response = self.app.get(V1_URL + '/users/10/location', headers={"UserToken" : "A fake token"})
		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 200)
		assert(response_parsed['user_loc'] == expected)

	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_10)
	@patch('src.main.com.ServerRequest.requests.get', side_effect=FakeGet)
	def test_get_userlocation_unauthorized(self, validateTokenMock, FakeGet):
		self.app = app.test_client()
		response = self.app.get(V1_URL + '/users/1/location', headers={"UserToken" : "A fake token"})
		assert(response.status_code == 403)

#	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_11)
#	def test_modify_userlocation_success(self, validateTokenMock):
#		current_loc = default_db[4]["coord"]
#		longitude = float(current_loc["long"])
#		latitude = float(current_loc["lat"])
#		newlat = random.uniform(0,latitude) if (latitude > 0) else random.uniform(latitude+1, 100)
#		newlong = random.uniform(0,longitude) if (longitude > 0) else random.uniform(longitude+1, 100)
#		new_loc = {"coord": {"lat": str(newlat), "long": str(newlong)}}

#		self.app = app.test_client()
#		response = self.app.put(V1_URL + '/users/11/location', headers={'UserToken' : "A fake token"}, data = json.dumps(new_loc), content_type='application/json')	
#		response_parsed = json.loads(response.get_data())
#		assert(response.status_code == 200)
#		assert(default_db[4]["coord"] == new_loc["coord"])

	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_10)
	@patch('src.main.com.ServerRequest.requests.get', side_effect=FakeGet)
	def test_get_driverrate_unauthorized(self, validateTokenMock, FakeGet):
		self.app = app.test_client()
		response = self.app.get(V1_URL + '/users/3/rating', headers={"UserToken" : "A fake token"})
		assert(response.status_code == 403)

	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_10)
	@patch('src.main.com.ServerRequest.requests.get', side_effect=FakeGet)
	def test_get_passengerrate_error(self, validateTokenMock, FakeGet):
		self.app = app.test_client()
		response = self.app.get(V1_URL + '/users/10/rating', headers={"UserToken" : "A fake token"})
		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 400)
		assert(response_parsed["message"] == "The requested user is not a driver. Only drivers receive ratings.")

	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_3)
	@patch('src.main.com.ServerRequest.requests.get', side_effect=FakeGet)
	def test_get_driverrate_success(self, validateTokenMock, FakeGet):
		expected = {}
		expected["_id"] = 3
		expected["rating"] = {"rate":0, "rateCount":0}

		self.app = app.test_client()
		response = self.app.get(V1_URL + '/users/3/rating', headers={"UserToken" : "A fake token"})
		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 200)
		assert(response_parsed['rating'] == expected)

"""
Some tests to add in the future:
	def test_insert_success(self):
	def test_insert_duplicate(self):
	def test_post_missing_id(self):
	def test_remove_success(self):
	def test_delete_invalid(self):
"""
