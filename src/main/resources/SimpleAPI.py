"""@package SimpleAPI
Documentation for this module.
More details.
"""

from flask_restful import Resource
from flask import jsonify, abort, request, make_response

import os
from pymongo import MongoClient
from src.main.log.Log import Logger

if os.environ.has_key('MONGODB_URL'):
    db_client = MongoClient(os.environ['MONGODB_URL'])
    print("Using remote database")
else:
    db_client = MongoClient("mongodb://127.0.0.1:27017/test")
db = db_client.get_default_database()
users = db.users

class Hello(Resource):
    """This class initializes a resource named Hello.
    It can be called through GET.
    """
    def get(self):
        print("GET at /")
        Logger.getLogger().debug("Hello Logger")
        return 'Hello' 

class GoodBye(Resource):
    """This class initializes a resource named Goodbye.
    It can be called through GET and POST.
    """
    def get(self):
        print("GET at /goodbye")
        Logger.getLogger().debug("Good Bye Logger")
        return 'Good Bye'

    def post(self):
        print("POST at /goodbye")
        return {'good':'bye'}

class Greet(Resource):
    """This class initializes a resource named Greet.
    It can be called through GET and DELETE.
    """

    def get(self, id):
        print("GET at /greet/id")
        candidates = [user for user in users.find() if user['_id'] == id]
        if len(candidates) == 0:
            Logger.getLogger().error("Attempted to retrieve user with non-existent id.")
            abort(404, 'user id not found')
        return jsonify({'greetings': candidates[0]})

    def delete(self, id):
        print(id)
        print("DELETE at /greet/id")

        candidates = [user for user in users.find() if user['_id'] == id]

        if len(candidates) == 0:
            Logger.getLogger().error("Attempted to delete user with non-existent id.")
            abort(404, 'user id not found')
        Logger.getLogger().info("Successfully deleted user.")
        users.delete_many({"_id" : candidates[0]['_id']})
        return jsonify({'user': candidates[0]})


class GreetAdd(Resource):
    """This class initializes a resource named GreetAdd.
    It can be called through GET and POST.
    """

    def get(self):
        print("GET at /greet")
        aux = [user for user in users.find()]
        return jsonify({'users' : aux})

    def post(self):
        print(request.json)
        if (not request.json or not 'user' in request.json):
            Logger.getLogger().error("Missing user data to create user.")
            abort(400, 'request missing user tag')
        if (not 'id' in  request.json['user']):
            Logger.getLogger().error("Attempted to create user without id.")
            abort(400, 'request missing id')
        if (not 'name' in request.json['user']):
            Logger.getLogger().error("Attempted to create user without name.")
            abort(400, 'request missing name')

        id = request.json['user']['id']

        for user in users.find():
            if user['_id'] == id:
                Logger.getLogger().error("Attempted to create user with existing id.")
                abort(400, 'user id already exists')

        name = request.json['user']['name']
        newUser = { '_id' : id, 'name' : name }

        users.insert_one(newUser)
        print("POST at /greet")
        return make_response(jsonify({'user' : newUser}), 201)

