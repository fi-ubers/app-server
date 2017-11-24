import json
import os
import jwt


V1_URL = '/v1/api'
MOCK_URL = 'http://172.17.0.2:80'
MOCK_TOKEN = '?token='
os.environ['SS_URL'] = MOCK_URL
os.environ["APP_TOKEN"] = "untokendementira"

MOCK_TOKEN_VALIDATION_1 = (True, {"username" : "juan", "_id" : 1})
MOCK_TOKEN_VALIDATION_2 = (False, "Invalid token: " + "A fake token")


from mock import Mock, patch
from src.main.com import ServerRequest, TokenGenerator
from src.main.resources import UserCars
from src.main.myApp import application as app

ServerRequest.QUERY_TOKEN = MOCK_TOKEN

paymethodsList = [{ "name": "Visa",  "parameters": { "number": "112233",  "type": "credit",  "expirationMonth": "01",  "expirationYear": "19",  "ccvv": "225"  } }]

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
		self.status_code = 0
		print(self.url +" vs "+ MOCK_URL + "/paymethods" + MOCK_TOKEN + os.environ["APP_TOKEN"])
		if (self.url == MOCK_URL + "/paymethods" + MOCK_TOKEN + os.environ["APP_TOKEN"]):
			self.status_code = 200
			self.response = {"paymethods" : paymethodsList }
		else:
			self.response = {"code" : 666, 'message' : 'Mocking error'}

	def json(self):
		return self.response


class TestPayment(object):

	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_2)
	def test_getall_user_paymethods_unauthorized(self, validateTokenMock):
		self.app = app.test_client()
		response = self.app.get(V1_URL + "/payment", headers={"UserToken" : "A fake token"})
		assert(response.status_code == 403)


	@patch('src.main.com.TokenGenerator.validateToken', return_value=MOCK_TOKEN_VALIDATION_1)
	@patch('src.main.com.ServerRequest.requests.get', side_effect=FakeGet)
	def test_getall_user_paymethods_authorized(self, validateTokenMock, FakeGet):
		expected = paymethodsList
		self.app = app.test_client()
		response = self.app.get(V1_URL + "/payment", headers={"UserToken" : "A fake token"})

		response_parsed = json.loads(response.get_data())

		assert response_parsed["paymethods"] == expected
		assert(response.status_code == 200)


