from flask_restful import Resource
from flask import jsonify, abort, request

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
            abort(404)
        return jsonify({'greetings': candidates[0]})



class GreetAdd(Resource):
    def get(self):
        print("GET at /greet")
        return jsonify({'users' : users})

    def post(self):
        print(request.json)
        if (not request.json or not 'user' in request.json):
            abort(400)
        if (not 'id' in  request.json['user'] or not 'name' in request.json['user']):
            abort(400)

        id = request.json['user']['id']

        for user in users:
            if user['id'] == id:
                abort(400)

        name = request.json['user']['name']
        newUser = { 'id' : id, 'name' : name }

        users.append(newUser)
        print("POST at /greet")
        return jsonify({'user' : newUser})
