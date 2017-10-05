import requests
import json

USER_END ="http://172.17.0.2:80/posts"
headers = {'Content-Type' : 'application/json'}


def test():
	r = requests.get(USER_END, headers=headers)	
	print(r.json())
	assert True

test()

