import json
import os
import jwt

V1_URL = "/v1/api"

MOCK_URL = "http://172.17.0.2:80"
MOCK_TOKEN = "?token="
MOCK_TOKEN_VALIDATION_DRV_IDLE = (True, {"username" : "user200", "_id" : 200})
MOCK_TOKEN_VALIDATION_PSG_SELECTING_DRIVER = (True, {"username" : "user102", "_id" : 102})
MOCK_TOKEN_VALIDATION_PSG_SELECTING_DRIVER_REJ = (True, {"username" : "user103", "_id" : 103})
MOCK_TOKEN_VALIDATION_PSG_STARTS_FIRST = (True, {"username" : "user103", "_id" : 104})
MOCK_TOKEN_VALIDATION_PSG_STARTS_SECOND = (True, {"username" : "user104", "_id" : 105})
MOCK_TOKEN_VALIDATION_DRV_STARTS_FIRST = (True, {"username" : "user205", "_id" : 205})
MOCK_TOKEN_VALIDATION_DRV_STARTS_SECOND = (True, {"username" : "user206", "_id" : 206})

MOCK_TOKEN_VALIDATION_PSG_FINISHS_FIRST = (True, {"username" : "user108", "_id" : 108})
MOCK_TOKEN_VALIDATION_PSG_FINISHS_SECOND = (True, {"username" : "user109", "_id" : 109})
MOCK_TOKEN_VALIDATION_DRV_FINISHS_FIRST = (True, {"username" : "user209", "_id" : 209})
MOCK_TOKEN_VALIDATION_DRV_FINISHS_SECOND = (True, {"username" : "user210", "_id" : 210})

MOCK_TOKEN_VALIDATION_PSG_RATES = (True, {"username" : "user112", "_id" : 112})
MOCK_TOKEN_VALIDATION_PSG_PAYS = (True, {"username" : "user113", "_id" : 113})

os.environ["SS_URL"] = MOCK_URL
os.environ["APP_TOKEN"] = "untokendementira"

from mock import Mock, patch
from CollectionMock import default_db, CollectionMock, trips_db
from src.main.mongodb import MongoController
MongoController.getCollection = Mock(side_effect = CollectionMock)

from src.main.com import ServerRequest, TokenGenerator
from src.main.resources import Trips
from src.main.myApp import application as app
from src.main.model import TripStates

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
		self.response = {"code" : 666, 'message' : 'Mocking error'}
	def json(self):
		return self.response

class FakePost(object):
	def __init__(self, url, headers={}, data=''):
		self.url = url
		self.db = default_db
		self.data = data
		ret = json.loads(self.data)
		if "paymethod" in ret.keys():
			if ret["paymethod"] == "cash":
				raise Exception
			elif ret["paymethod"] =="card":
				self.status_code = 201
			else:
				self.status_code = 400
		self.response = {"code" : 666, 'message' : 'Mocking error'}
	def json(self):
		return self.response

class TestTripAction(object):
	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_DRV_IDLE)
	def test_driver_accept_trip_success(self, validateTokenMock):
		action = { "action" : TripStates.ACTION_DRIVER_ACCEPT }
		self.app = app.test_client()
		response = self.app.post(V1_URL + "/trips/2/action", headers={"UserToken" : "A fake token"}, data=json.dumps(action), content_type='application/json')
		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 200)
		assert("trip" in response_parsed)
		trip = response_parsed["trip"]
		assert(trip["state"] == TripStates.TRIP_ACCEPTED)
		assert(trip["driverId"] == MOCK_TOKEN_VALIDATION_DRV_IDLE[1]["_id"])

	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_DRV_IDLE)
	def test_driver_accept_trip_state_error(self, validateTokenMock):
		action = { "action" : TripStates.ACTION_DRIVER_ACCEPT }
		self.app = app.test_client()
		response = self.app.post(V1_URL + "/trips/3/action", headers={"UserToken" : "A fake token"}, data=json.dumps(action), content_type='application/json')
		response_parsed = json.loads(response.get_data())
		assert(response.status_code == 400)
		assert("Bad request" in response_parsed["message"])

	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_PSG_SELECTING_DRIVER)
	def test_driver_confirm_trip_success(self, validateTokenMock):
		action = { "action" : TripStates.ACTION_PASSENGER_CONFIRM }
		self.app = app.test_client()
		response = self.app.post(V1_URL + "/trips/3/action", headers={"UserToken" : "A fake token"}, data=json.dumps(action), content_type='application/json')
		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 200)
		assert("trip" in response_parsed)
		trip = response_parsed["trip"]
		assert(trip["state"] == TripStates.TRIP_CONFIRMED)

	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_PSG_SELECTING_DRIVER)
	def test_passenger_confirm_trip_error_bad_state(self, validateTokenMock):
		action = { "action" : TripStates.ACTION_PASSENGER_CONFIRM }
		self.app = app.test_client()
		response = self.app.post(V1_URL + "/trips/3/action", headers={"UserToken" : "A fake token"}, data=json.dumps(action), content_type='application/json')
		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 400)

	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_PSG_SELECTING_DRIVER_REJ)
	def test_passenger_reject_driver(self, validateTokenMock):
		action = { "action" : TripStates.ACTION_PASSENGER_REJECT }
		self.app = app.test_client()
		response = self.app.post(V1_URL + "/trips/4/action", headers={"UserToken" : "A fake token"}, data=json.dumps(action), content_type='application/json')
		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 200)
		assert("trip" in response_parsed)
		trip = response_parsed["trip"]
		assert(trip["state"] == TripStates.TRIP_PROPOSED)

	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_PSG_STARTS_FIRST)
	def test_passenger_starts_first(self, validateTokenMock):
		action = { "action" : TripStates.ACTION_START }
		self.app = app.test_client()
		response = self.app.post(V1_URL + "/trips/5/action", headers={"UserToken" : "A fake token"}, data=json.dumps(action), content_type='application/json')
		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 200)
		assert("trip" in response_parsed)
		trip = response_parsed["trip"]
		assert(trip["state"] == TripStates.TRIP_STARTED_PASSENGER)

	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_PSG_STARTS_SECOND)
	def test_passenger_starts_second(self, validateTokenMock):
		action = { "action" : TripStates.ACTION_START }
		self.app = app.test_client()
		response = self.app.post(V1_URL + "/trips/6/action", headers={"UserToken" : "A fake token"}, data=json.dumps(action), content_type='application/json')
		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 200)
		assert("trip" in response_parsed)
		trip = response_parsed["trip"]
		assert(trip["state"] == TripStates.TRIP_STARTED)

	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_DRV_STARTS_FIRST)
	def test_driver_starts_first(self, validateTokenMock):
		action = { "action" : TripStates.ACTION_START }
		self.app = app.test_client()
		response = self.app.post(V1_URL + "/trips/7/action", headers={"UserToken" : "A fake token"}, data=json.dumps(action), content_type='application/json')
		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 200)
		assert("trip" in response_parsed)
		trip = response_parsed["trip"]
		assert(trip["state"] == TripStates.TRIP_STARTED_DRIVER)

	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_DRV_STARTS_SECOND)
	def test_driver_starts_second(self, validateTokenMock):
		action = { "action" : TripStates.ACTION_START }
		self.app = app.test_client()
		response = self.app.post(V1_URL + "/trips/8/action", headers={"UserToken" : "A fake token"}, data=json.dumps(action), content_type='application/json')
		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 200)
		assert("trip" in response_parsed)
		trip = response_parsed["trip"]
		assert(trip["state"] == TripStates.TRIP_STARTED)

	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_PSG_FINISHS_FIRST)
	def test_passenger_finishs_first(self, validateTokenMock):
		action = { "action" : TripStates.ACTION_FINISH }
		self.app = app.test_client()
		response = self.app.post(V1_URL + "/trips/9/action", headers={"UserToken" : "A fake token"}, data=json.dumps(action), content_type='application/json')
		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 200)
		assert("trip" in response_parsed)
		trip = response_parsed["trip"]
		assert(trip["state"] == TripStates.TRIP_FINISHED_PASSENGER)

	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_PSG_FINISHS_SECOND)
	def test_passenger_finishs_second(self, validateTokenMock):
		action = { "action" : TripStates.ACTION_FINISH }
		self.app = app.test_client()
		response = self.app.post(V1_URL + "/trips/10/action", headers={"UserToken" : "A fake token"}, data=json.dumps(action), content_type='application/json')
		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 200)
		assert("trip" in response_parsed)
		trip = response_parsed["trip"]
		assert(trip["state"] == TripStates.TRIP_FINISHED)

	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_DRV_FINISHS_FIRST)
	def test_driver_finishs_first(self, validateTokenMock):
		action = { "action" : TripStates.ACTION_FINISH }
		self.app = app.test_client()
		response = self.app.post(V1_URL + "/trips/11/action", headers={"UserToken" : "A fake token"}, data=json.dumps(action), content_type='application/json')
		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 200)
		assert("trip" in response_parsed)
		trip = response_parsed["trip"]
		assert(trip["state"] == TripStates.TRIP_FINISHED_DRIVER )

	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_DRV_FINISHS_SECOND)
	def test_driver_finishs_second(self, validateTokenMock):
		action = { "action" : TripStates.ACTION_FINISH }
		self.app = app.test_client()
		response = self.app.post(V1_URL + "/trips/12/action", headers={"UserToken" : "A fake token"}, data=json.dumps(action), content_type='application/json')
		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 200)
		assert("trip" in response_parsed)
		trip = response_parsed["trip"]
		assert(trip["state"] == TripStates.TRIP_FINISHED)

	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_PSG_RATES)
	def test_passenger_rates_missing_rating(self, validateTokenMock):
		action = { "action" : TripStates.ACTION_RATE}
		self.app = app.test_client()
		response = self.app.post(V1_URL + "/trips/13/action", headers={"UserToken" : "A fake token"}, data=json.dumps(action), content_type='application/json')
		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 400)

	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_PSG_RATES)
	def test_passenger_rates_driver_invalid(self, validateTokenMock):
		action = { "action" : TripStates.ACTION_RATE, "rating" : 17 }
		self.app = app.test_client()
		response = self.app.post(V1_URL + "/trips/13/action", headers={"UserToken" : "A fake token"}, data=json.dumps(action), content_type='application/json')
		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 400)

	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_PSG_RATES)
	def test_passenger_rates_driver_valid(self, validateTokenMock):
		action = { "action" : TripStates.ACTION_RATE, "rating" : 4 }
		self.app = app.test_client()
		response = self.app.post(V1_URL + "/trips/13/action", headers={"UserToken" : "A fake token"}, data=json.dumps(action), content_type='application/json')
		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 200)
		assert("trip" in response_parsed)
		trip = response_parsed["trip"]
		assert(trip["state"] == TripStates.TRIP_FINISHED_RATED)

	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_PSG_PAYS)
	@patch("src.main.com.ServerRequest.requests.post", side_effect=FakePost)
	def test_passenger_invalid_payment(self, validateTokenMock, FakePost):
		action = { "action" : TripStates.ACTION_PAY, "paymethod" : "nothing" }
		self.app = app.test_client()
		response = self.app.post(V1_URL + "/trips/14/action", headers={"UserToken" : "A fake token"}, data=json.dumps(action), content_type='application/json')
		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 400)

	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_PSG_PAYS)
	@patch("src.main.com.ServerRequest.requests.post", side_effect=FakePost)
	def test_passenger_pays_unexpected_error(self, validateTokenMock, FakePost):
		action = { "action" : TripStates.ACTION_PAY, "paymethod" : "cash" }
		self.app = app.test_client()
		response = self.app.post(V1_URL + "/trips/14/action", headers={"UserToken" : "A fake token"}, data=json.dumps(action), content_type='application/json')
		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 500)

	@patch("src.main.com.TokenGenerator.validateToken", return_value=MOCK_TOKEN_VALIDATION_PSG_PAYS)
	@patch("src.main.com.ServerRequest.requests.post", side_effect=FakePost)
	def test_passenger_pays_success(self, validateTokenMock, FakePost):
		action = { "action" : TripStates.ACTION_PAY, "paymethod" : "card" }
		self.app = app.test_client()
		response = self.app.post(V1_URL + "/trips/14/action", headers={"UserToken" : "A fake token"}, data=json.dumps(action), content_type='application/json')
		response_parsed = json.loads(response.get_data())
		print(response_parsed)
		assert(response.status_code == 201)
