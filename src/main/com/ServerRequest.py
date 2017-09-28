import logging as logger

def validateUser(user_js):
	if user_js['password'] == "1234":
		logger.getLogger().debug("User found!!")
		return { "_id" : 1, "username" : "juan", "birthdate": "18/07/1994", "firstname" : "Juan"}
	else:
		logger.getLogger().debug("User no valid!!")
		return None 
