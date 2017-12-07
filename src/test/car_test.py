import json
import os
import jwt

V1_URL = '/v1/api'
MOCK_URL = 'http://172.17.0.2:80'
MOCK_TOKEN = '?token='
MOCK_TOKEN_VALIDATION_1 = (True, {"username" : "juan", "_id" : 1})
MOCK_TOKEN_VALIDATION_2 = (True, {"username" : "juanpi", "_id" : 2})
MOCK_TOKEN_VALIDATION_3 = (True, {"username" : "euge", "_id" : 3})
MOCK_TOKEN_VALIDATION_7 = (True, {"username" : "luis", "_id" : 7})

os.environ['SS_URL'] = MOCK_URL
os.environ["APP_TOKEN"] = "untokendementira"

from mock import Mock, patch
from CollectionMock import CollectionMock, default_db
from src.main.mongodb import MongoController
MongoController.getCollection = Mock(side_effect = CollectionMock)


from src.main.com import ServerRequest, TokenGenerator
from src.main.resources import UserCars
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
		if (self.url == MOCK_URL + "/users/1/cars"):
			self.status_code = 200
			self.response = {'code' : self.status_code, "cars" : self.db[0]["cars"]}
		elif (self.url == MOCK_URL + '/users/2'):
			self.status_code = 401
			self.response = {"code" : 401, 'message' : 'Unauthorized'}
		elif (self.url == MOCK_URL + '/users/3'):
			self.status_code = 500
			self.response = {"code" : 500, 'message' : 'Unexpected error'}
		elif (self.url == MOCK_URL + '/users/1/cars/12' + MOCK_TOKEN + os.environ["APP_TOKEN"]):
			self.status_code = 200
			self.response = {'code' : self.status_code, "car" : self.db[0]["cars"][0]}
		elif (self.url == MOCK_URL + '/users/3/cars/17' + MOCK_TOKEN + os.environ["APP_TOKEN"]):
			self.status_code = 500
			self.response = {'code' : self.status_code, "message" : "Unexpected error"}
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
		if (self.url == MOCK_URL + "/users/1/cars" + MOCK_TOKEN + os.environ["APP_TOKEN"]):
			self.status_code = 201
			self.response = {"code" : self.status_code, "car" : json.loads(self.data)}
		elif (self.url == MOCK_URL + "/users/2/cars" + MOCK_TOKEN + os.environ["APP_TOKEN"]):
			self.status_code = 500
			self.response = {"code" : self.status_code, "message" : "Unexpected error"}
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

		if (self.url == MOCK_URL + '/users/1/cars/12' + MOCK_TOKEN + os.environ["APP_TOKEN"]):
			self.status_code = 204
			self.response = { "code" : self.status_code, 'message' : 'delete successful'}
		elif (self.url == MOCK_URL + '/users/2/cars/13' + MOCK_TOKEN + os.environ["APP_TOKEN"]):
			self.status_code = 404
			self.response = { "code" : self.status_code, 'message' : 'non-existent id'}
		elif (self.url == MOCK_URL + "/users/2/cars/14" + MOCK_TOKEN + os.environ["APP_TOKEN"]):
			self.status_code = 500
			self.response = {"code" : self.status_code, "message" : "Unexpected error"}
		else:
			self.response = {"code" : 666, 'message' : 'Mocking error'}

	def json(self):
		return self.response

class TestCarsCRUD(object):

	def test_getall_user_cars_unauthorized(self):
		expected = "Bad request - missing token"
		self.app = app.test_client()
		response = self.app.get(V1_URL + '/users/1/cars')

		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 400)
		assert(response_parsed["message"] == expected)
		assert(response_parsed["code"] == 400)

	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_1)
	def test_getall_user_cars_unauthorized(self, validateTokenMock):
		self.app = app.test_client()
		response = self.app.get(V1_URL + '/users/2/cars', headers={"UserToken" : "A fake token"})
		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 403)


	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_1)
	@patch('src.main.com.ServerRequest.requests.get', side_effect=FakeGet)
	def test_getall_user_cars_authorized(self, validateTokenMock, FakeGet):
		expected = default_db[0]

		self.app = app.test_client()
		response = self.app.get(V1_URL + '/users/1/cars', headers={"UserToken" : "A fake token"})

		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 200)
		assert(response_parsed['cars'] == expected['cars'][0])

	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_1)
	@patch('src.main.com.ServerRequest.requests.post', side_effect=FakePost)
	def test_register_new_car_success(self, validateTokenMock, FakePost):
		expected = {"name": "Ferrari", "value": "HBP111" }
		self.app = app.test_client()
		response = self.app.post(V1_URL + '/users/1/cars', headers={"UserToken" : "A fake token"}, data = json.dumps(expected), content_type='application/json')

		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 201)
		assert(response_parsed["car"]["properties"][0] == expected)

	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_1)
	@patch('src.main.com.ServerRequest.requests.post', side_effect=FakePost)
	def test_register_new_car_unauthorized(self, validateTokenMock, FakePost):
		expected = {"name": "Ferrari", "value": "HBP111" }
		self.app = app.test_client()
		response = self.app.post(V1_URL + '/users/2/cars', headers={"UserToken" : "A fake token"}, data = json.dumps(expected), content_type='application/json')
		response_parsed = json.loads(response.get_data())

		assert(response.status_code == 403)
		assert(response_parsed["message"] == "Forbidden")


	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_2)
	@patch('src.main.com.ServerRequest.requests.post', side_effect=FakePost)
	def test_register_new_car_fail(self, validateTokenMock, FakePost):
		expected = {"name": "Ferrari", "value": "HBP111" }
		self.app = app.test_client()
		response = self.app.post(V1_URL + '/users/2/cars', headers={"UserToken" : "A fake token"}, data = json.dumps(expected), content_type='application/json')
		response_parsed = json.loads(response.get_data())

		assert(response.status_code == 500)
		assert(response_parsed["message"] == "Unexpected error")

	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_2)
	def test_get_car_by_id_unauthorized(self, validateTokenMock):
		self.app = app.test_client()
		response = self.app.get(V1_URL + '/users/1/cars/12', headers={"UserToken" : "A fake token"})
		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 403)


	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_1)
	@patch('src.main.com.ServerRequest.requests.get', side_effect=FakeGet)
	def test_get_car_by_id_success(self, validateTokenMock, FakeGet):
		expected = default_db[0]["cars"][0]["properties"][0]

		self.app = app.test_client()
		response = self.app.get(V1_URL + '/users/1/cars/12', headers={"UserToken" : "A fake token"})

		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 200)
		assert(response_parsed['car'] == expected)


	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_3)
	@patch('src.main.com.ServerRequest.requests.get', side_effect=FakeGet)
	def test_get_car_by_id_error(self, validateTokenMock, FakeGet):
		expected = default_db[0]["cars"][0]["properties"][0]

		self.app = app.test_client()
		response = self.app.get(V1_URL + '/users/3/cars/17', headers={"UserToken" : "A fake token"})

		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 500)
		assert(response_parsed["message"] == "Unexpected error")


	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_1)
	@patch('src.main.com.ServerRequest.requests.delete', side_effect=FakeDelete)
	def test_delete_car_success(self, validateTokenMock, FakeDelete):
		self.app = app.test_client()
		response = self.app.delete(V1_URL + '/users/1/cars/12', headers={"UserToken" : "A fake token"}, content_type='application/json')
		assert(response.status_code == 204)


	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_2)
	@patch('src.main.com.ServerRequest.requests.delete', side_effect=FakeDelete)
	def test_delete_car_nonexistent(self, validateTokenMock, FakeDelete):
		self.app = app.test_client()
		response = self.app.delete(V1_URL + '/users/2/cars/13', headers={"UserToken" : "A fake token"}, content_type='application/json')
		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 404)


	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_2)
	@patch('src.main.com.ServerRequest.requests.delete', side_effect=FakeDelete)
	def test_delete_car_unauthorized(self, validateTokenMock, FakeDelete):
		self.app = app.test_client()
		response = self.app.delete(V1_URL + '/users/1/cars/12', headers={"UserToken" : "A fake token"}, content_type='application/json')

		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 403)
		assert(response_parsed["message"] == "Forbidden")


	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_2)
	@patch('src.main.com.ServerRequest.requests.delete', side_effect=FakeDelete)
	def test_delete_car_error(self, validateTokenMock, FakeDelete):
		self.app = app.test_client()
		response = self.app.delete(V1_URL + '/users/2/cars/14', headers={"UserToken" : "A fake token"}, content_type='application/json')

		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 500)
		assert(response_parsed["message"] == "Unexpected error")
