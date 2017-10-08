import jwt

SECRET_KEY = 'red_fox'

def generateToken(user):
	print(user)
	payload = {}
	payload['username'] = user['username']
	token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
	return token

def validateToken(token):
	try:
		decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
	except:
		return (False, "Invalid")
	return (True, decoded)
