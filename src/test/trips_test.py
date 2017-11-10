import json
import os
import jwt

V1_URL = "/v1/api"

MOCK_URL = "http://172.17.0.2:80"
MOCK_TOKEN = "?token=untokendementira"
MOCK_TOKEN_VALIDATION_1 = (True, {"username" : "juan", "_id" : 1})
MOCK_TOKEN_VALIDATION_2 = (True, {"username" : "juanpi", "_id" : 2})
MOCK_TOKEN_VALIDATION_7 = (True, {"username" : "luis", "_id" : 7})

os.environ["SS_URL"] = MOCK_URL

from mock import Mock, patch
from CollectionMock import UserCollectionMock, default_db
from src.main.mongodb import MongoController
MongoController.getCollection = Mock(return_value = UserCollectionMock())

from src.main.com import ServerRequest, TokenGenerator
from src.main.resources import Trips
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

		if (self.url == MOCK_URL + '/users/1/trips' + MOCK_TOKEN):
			self.status_code = 200
			self.response = {'code' : self.status_code, 'trips' : self.db[0]["trips"] }
		elif (self.url == MOCK_URL + '/users/2/trips' + MOCK_TOKEN):
			self.status_code = 500
			self.response = {'code' : self.status_code, 'message' : "Unknown Error"}
		elif (self.url == MOCK_URL + '/users/7/trips' + MOCK_TOKEN):
			self.status_code = 404
			self.response = {'code' : self.status_code, 'message' : "NOT FOUND"}
		else:
			self.status_code = 666
			self.response = {"code" : 666, 'message' : 'Mocking error'}

	def json(self):
		return self.response

class FakePost(object):
	def __init__(self, url, headers={}, data=''):
		self.url = url
		self.db = default_db
		self.data = data
		self.status_code = 0
		if (self.url == MOCK_URL + '/trips' + MOCK_TOKEN):
			ret = json.loads(self.data)
			if ret["id"] == "1":
				self.status_code = 500
				self.response = {"code" : self.status_code, 'message' : 'Unknown Error'}
			else:
				self.status_code = 201
				self.response = { "code" : self.status_code, "trip" : ret }
		else:
			self.response = {"code" : 666, 'message' : 'Mocking error'}

	def json(self):
		return self.response


class TestUsertrips(object):
	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_2)
	def test_getall_user_trips_unauthorized(self, validateTokenMock):
		self.app = app.test_client()
		response = self.app.get(V1_URL + "/users/1/trips", headers={"UserToken" : "A fake token"})
		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 403)


	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_1)
	@patch("src.main.com.ServerRequest.requests.get", side_effect=FakeGet)
	def test_getall_user_trips_success(self, validateTokenMock, FakeGet):
		expected = default_db[0]

		self.app = app.test_client()
		response = self.app.get(V1_URL + "/users/1/trips", headers={"UserToken" : "A fake token"})

		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 200)
		assert(response_parsed["trips"] == expected["trips"])

	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_7)
	@patch("src.main.com.ServerRequest.requests.get", side_effect=FakeGet)
	def test_getall_user_trips_nonexistent_user(self, validateTokenMock, FakeGet):
		self.app = app.test_client()
		response = self.app.get(V1_URL + "/users/7/trips", headers={"UserToken" : "A fake token"})

		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 404)

	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_2)
	@patch("src.main.com.ServerRequest.requests.get", side_effect=FakeGet)
	def test_getall_user_trips_error(self, validateTokenMock, FakeGet):
		self.app = app.test_client()
		response = self.app.get(V1_URL + "/users/2/trips", headers={"UserToken" : "A fake token"})

		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 500)
		assert(response_parsed["message"] == "Unknown Error")

	@patch("src.main.com.ServerRequest.requests.post", side_effect=FakePost)
	def test_new_trip_error(self, FakePost):
		expected = default_db[0]["trips"][0]

		self.app = app.test_client()
		response = self.app.post(V1_URL + "/trips", headers={"UserToken" : "A fake token"}, data = json.dumps(expected), content_type='application/json')

		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 500)
		assert(response_parsed["message"] == "Unknown Error")

	@patch("src.main.com.ServerRequest.requests.post", side_effect=FakePost)
	def test_new_trip_success(self, FakePost):
		expected = default_db[1]["trips"][0]
		self.app = app.test_client()
		response = self.app.post(V1_URL + "/trips", headers={"UserToken" : "A fake token"}, data = json.dumps(expected), content_type='application/json')

		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 201)
		assert(response_parsed["trip"] == expected)