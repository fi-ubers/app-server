import json
import os
import jwt

V1_URL = '/v1/api'
MOCK_URL = 'http://172.17.0.2:80'
MOCK_TOKEN = '?token='

os.environ['SS_URL'] = MOCK_URL
os.environ["APP_TOKEN"] = "untokendementira"

from mock import Mock, patch
from src.main.com import Server
from datetime import datetime

Server.QUERY_TOKEN = MOCK_TOKEN

server_info = { "server": { "id": "1", "_ref": "aasd", "createdBy": "Gandalf", "createdTime": 0, "name": "SS1", "lastConnection": 0 }, "token": { "expiresAt": datetime.today() , "token": "abc123" } }

class FakeGet(object):
	def __init__(self, url, headers={}):
		self.url = url
		self.headers = headers
		self.status_code = 0
		if (self.url == MOCK_URL + "/server/ping" + MOCK_TOKEN + os.environ["APP_TOKEN"]):
			self.status_code = 200
			self.response = {"code" : self.status_code, "ping" : server_info}
		else:
			self.response = {"code" : 666, 'message' : 'Mocking error'}

	def json(self):
		return self.response

class FakeGetError(object):
	def __init__(self, url, headers={}):
		self.url = url
		self.headers = headers
		self.status_code = 0
		if (self.url == MOCK_URL + "/server/ping" + MOCK_TOKEN + os.environ["APP_TOKEN"]):
			self.status_code = 500
			self.response = {"code" : self.status_code, "ping" : server_info}
		else:
			self.response = {"code" : 666, 'message' : 'Mocking error'}

	def json(self):
		return self.response


class TestServer(object):

	@patch('src.main.com.Server.requests.get', side_effect=FakeGet)
	def test_ping_server_success(self, FakeGet):
		server = Server.ServerTokenUpdater()
		server_response = server.updateToken()
		assert server_response == server_info["server"]
	
	@patch('src.main.com.Server.requests.get', side_effect=FakeGetError)
	def test_ping_server_error(self, FakeGetError):
		server = Server.ServerTokenUpdater()
		server_response = server.updateToken()
		assert server_response["error"] == 500









