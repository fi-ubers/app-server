import jwt

SECRET_KEY = 'red_fox'

def generateToken(user):
	print(user)
	if (not user) or (not 'username' in user) or (not '_id' in user):
		raise Exception("Invalid user: missing fields")
	payload = {}
	payload['username'] = user['username']
	payload['_id'] = user['_id']
	token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
	return token

def validateToken(token):
	try:
		decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
	except Exception as e:
		return (False, "Invalid token: " + str(e))
	return (True, decoded)

