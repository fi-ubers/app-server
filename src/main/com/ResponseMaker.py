from flask import jsonify, make_response

def response_error(code, message):
	return make_response(jsonify({'code' : code, 'message' : message}), code)

def response_object(code, tags, objs):
	if (len(tags) != len(objs)):
		raise Exception("response_multiple error: len(tags) != len(objs)")
	response = {'code' : code}
	for (k, v) in zip(tags, objs):
		response[k] = v
	return make_response(jsonify(response), code)
