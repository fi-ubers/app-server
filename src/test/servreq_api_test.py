import requests
import json

USER_END ="http://172.17.0.2:80/posts"
headers = {'Content-Type' : 'application/json'}

class TestServerRequest():

	def test(self):
		expected = [  {'id': 1,'title': 'json-server','author': 'typicode' }]
		r = requests.get(USER_END, headers=headers)
		assert ( r.json() == expected )


