from flask import Flask
from flask_restful import Resource, Api

import src.main.mongodb.MongoController

from src.main.resources.SimpleAPI import Hello, GoodBye, Greet, GreetAdd
from src.main.resources.UserLogin import UserLogin

application = Flask(__name__)
api = Api(application)

api.add_resource(Hello, '/')
api.add_resource(GoodBye, '/goodbye')
api.add_resource(Greet, '/greet/<int:id>')
api.add_resource(GreetAdd, '/greet')
api.add_resource(UserLogin, '/users/login')

if __name__ == "__main__":
    application.run(host='localhost')

