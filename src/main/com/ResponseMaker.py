from flask import jsonify, make_response

def response(code, message):
	return make_response(jsonify({'code' : code, 'message' : message}), code)
