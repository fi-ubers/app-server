import jwt

SECRET_KEY = 'red_fox'

def generateToken(user):
	payload = {}
	payload['username'] = user['username']
	payload['password'] = user['password']
	token = jwt.encode(payload, SECRET_KEY, algotithm='HS256')

def validateToken(user, token):
	generated = generateToken(user)
	return generated == token
