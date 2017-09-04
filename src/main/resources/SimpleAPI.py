from flask_restful import Resource
from flask import jsonify, abort, request, make_response

class Hello(Resource):
    def get(self):
        print("GET at /")
        return 'Hello' 

class GoodBye(Resource):
    def get(self):
        print("GET at /goodbye")
        return 'Good Bye'

    def post(self):
        print("POST at /goodbye")
        return {'good':'bye'}


users = [
        { 'id': 1, 'name': "Juan"},
        { 'id': 2, 'name': "Ale"},
        { 'id': 3, 'name': "Cami"},
        { 'id': 6, 'name': "Euge"}
    ]

class Greet(Resource):
    def get(self, id):
        print("GET at /greet/id")
        candidates = [user for user in users if user['id'] == id]
        if len(candidates) == 0:
            abort(404, 'user id not found')
        return jsonify({'greetings': candidates[0]})

    def delete(self, id):
        print(request.json)
        print("DELETE at /greet/id")

        candidates = [user for user in users if user['id'] == id]

        if len(candidates) == 0:
            abort(404, 'user id not found')

        users.remove(candidates[0])
        return jsonify({'user': candidates[0]})


class GreetAdd(Resource):
    def get(self):
        print("GET at /greet")
        return jsonify({'users' : users})

    def post(self):
        print(request.json)
        if (not request.json or not 'user' in request.json):
            abort(400, 'request missing user tag')
        if (not 'id' in  request.json['user']):
            abort(400, 'request missing id')
        if (not 'name' in request.json['user']):
            abort(400, 'request missing name')

        id = request.json['user']['id']

        for user in users:
            if user['id'] == id:
                abort(400, 'user id already exists')

        name = request.json['user']['name']
        newUser = { 'id' : id, 'name' : name }

        users.append(newUser)
        print("POST at /greet")
        return make_response(jsonify({'user' : newUser}), 201)

