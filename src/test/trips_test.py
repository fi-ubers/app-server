import json
import os
import jwt

V1_URL = "/v1/api"

MOCK_URL = "http://172.17.0.2:80"
MOCK_TOKEN = "?token="
MOCK_TOKEN_VALIDATION_1 = (True, {"username" : "juan", "_id" : 1})
MOCK_TOKEN_VALIDATION_2 = (True, {"username" : "juanpi", "_id" : 2})
MOCK_TOKEN_VALIDATION_7 = (True, {"username" : "luis", "_id" : 7})
MOCK_TOKEN_VALIDATION_8 = (False, "Invalid token: " + "A fake token")

os.environ["SS_URL"] = MOCK_URL
os.environ["APP_TOKEN"] = "untokendementira"

from mock import Mock, patch
from CollectionMock import default_db, CollectionMock, trips_db
from src.main.mongodb import MongoController
MongoController.getCollection = Mock(side_effect = CollectionMock)

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
		print(str(self.url) + "vs" + str(MOCK_URL + '/users/1/trips' + MOCK_TOKEN + os.environ["APP_TOKEN"]) )
		if (self.url == MOCK_URL + '/users/1/trips' + MOCK_TOKEN + os.environ["APP_TOKEN"]):
			self.status_code = 200
			self.response = {'code' : self.status_code, 'trips' : self.db[0]["trips"] }
		elif (self.url == MOCK_URL + '/users/2/trips' + MOCK_TOKEN + os.environ["APP_TOKEN"]):
			self.status_code = 500
			self.response = {'code' : self.status_code, 'message' : "Unknown Error"}
		elif (self.url == MOCK_URL + '/users/7/trips' + MOCK_TOKEN + os.environ["APP_TOKEN"]):
			self.status_code = 404
			self.response = {'code' : self.status_code, 'message' : "NOT FOUND"}

		elif (self.url == MOCK_URL + '/trips/1' + MOCK_TOKEN + os.environ["APP_TOKEN"]):
			self.status_code = 200
			self.response = {'code' : self.status_code, 'trip': self.db[0]["trips"][0]}
		elif (self.url == MOCK_URL + '/trips/2' + MOCK_TOKEN + os.environ["APP_TOKEN"]):
			self.status_code = 500
			self.response = {'code' : self.status_code, 'message' : "Unknown Error"}
		elif (self.url == MOCK_URL + '/trips/12555' + MOCK_TOKEN + os.environ["APP_TOKEN"]):
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
		if (self.url == MOCK_URL + '/trips' + MOCK_TOKEN + os.environ["APP_TOKEN"]):
			ret = json.loads(self.data)
			if ret["id"] == "1":
				self.status_code = 500
				self.response = {"code" : self.status_code, 'message' : 'Unknown Error'}
			else:
				self.status_code = 201
				self.response = { "code" : self.status_code, "trip" : ret }
		elif (self.url == MOCK_URL + '/trips/estimate' + MOCK_TOKEN + os.environ["APP_TOKEN"]):
			ret = json.loads(self.data)
			if ret["id"] == '1':
				self.status_code = 200
				self.response = { "cost" : {"currency": "dollar", "value": "200" } }		
			else:
				self.status_code = 500
				self.response = {"code" : self.status_code, 'message' : 'Unknown Error'}
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
		assert(response.status_code == 401)

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

	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_8)
	def test_get_trip_by_id_unauthorized(self, validateTokenMock):
		self.app = app.test_client()
		response = self.app.get(V1_URL + "/trips/1", headers={"UserToken" : "A fake token"})
		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 401)


	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_1)
	@patch("src.main.com.ServerRequest.requests.get", side_effect=FakeGet)
	def test_get_trip_by_id_success(self, validateTokenMock, FakeGet):
		expected = trips_db[0]
		self.app = app.test_client()
		response = self.app.get(V1_URL + "/trips/1", headers={"UserToken" : "A fake token"})
		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 200)
		assert(response_parsed["trip"] == expected)

	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_1)
	@patch("src.main.com.ServerRequest.requests.get", side_effect=FakeGet)
	def test_get_trip_by_id_nonexistent(self, validateTokenMock, FakeGet):
		self.app = app.test_client()
		response = self.app.get(V1_URL + "/trips/12555", headers={"UserToken" : "A fake token"})
		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 404)
		assert(response_parsed['message'] == "Not found")
		
	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_1)
	@patch("src.main.com.ServerRequest.requests.post", side_effect=FakePost)
	def test_estimate_trip_success(self,validateTokenMock, FakePost):
		trip = default_db[0]["trips"][0]
		expected = {"cost": {"currency": "dollar", "value": "200" }}
		self.app = app.test_client()
		response = self.app.post(V1_URL + "/trips/estimation", headers={"UserToken" : "A fake token"}, data = json.dumps(trip), content_type='application/json')
		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 200)
		assert(response_parsed["cost"] == expected)

	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_1)
	@patch("src.main.com.ServerRequest.requests.post", side_effect=FakePost)
	def test_estimate_trip_error(self,validateTokenMock, FakePost):
		trip = default_db[1]["trips"][0]
		self.app = app.test_client()
		response = self.app.post(V1_URL + "/trips/estimation", headers={"UserToken" : "A fake token"}, data = json.dumps(trip), content_type='application/json')
		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 500)
		assert(response_parsed["message"] == "Unknown Error")

	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_8)
	def test_estimate_trip_unauthorized(self,validateTokenMock):
		trip = default_db[1]["trips"][0]
		self.app = app.test_client()
		response = self.app.post(V1_URL + "/trips/estimation", headers={"UserToken" : "A fake token"}, data = json.dumps(trip), content_type='application/json')
		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 403)
		assert(response_parsed["message"] == "Forbidden")

	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_1)
	@patch("src.main.com.ServerRequest.requests.post", side_effect=FakePost)
	def test_new_trip_success_offline(self, validateTokenMock):
		directions = {}
		self.app = app.test_client()
		response = self.app.post(V1_URL + "/trips", headers={"UserToken" : "A fake token"}, data = json.dumps(directions), content_type='application/json')
		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 400)
		assert("Bad request" in response_parsed["message"])
	


	
