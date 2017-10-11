import os
import json
import mock
import requests
from src.main.com import ServerRequest

headers = {'Content-Type' : 'application/json'}

class TestServerRequest():

	@mock.patch.dict(os.environ, {"SS_URL": "http://localhost:1777"})
	def test_getusers_returns_userlist(self):
		pass
	"""
		expected_email = "voldyvoldy@hotmail.com"
		assert(ServerRequest.getUsers()[0]["email"] == "voldyvoldy@hotmail.com" )
	"""
