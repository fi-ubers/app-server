from flask import Flask
from flask_restful import Resource, Api

import src.main.mongodb.MongoController

from src.main.resources.SimpleAPI import Hello, GoodBye, GreetAdd, DriversList
from src.main.resources.UserLogin import UserLogin, UsersList, UserLogout, UserById

application = Flask(__name__)
api = Api(application)

api.add_resource(Hello, '/')
api.add_resource(GreetAdd, '/greet')
api.add_resource(GoodBye, '/goodbye')
api.add_resource(UserById, '/users/<int:id>')
api.add_resource(UserLogin, '/users/login')
api.add_resource(UserLogout, '/users/logout')
api.add_resource(UsersList, '/users')
api.add_resource(DriversList, '/users/drivers')


if __name__ == "__main__":
    application.run(host='localhost')

