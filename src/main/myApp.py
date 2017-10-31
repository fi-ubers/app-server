from flask import Flask
from flask_restful import Resource, Api

import src.main.mongodb.MongoController

from src.main.resources.SimpleAPI import Hello, GoodBye, GreetAdd
from src.main.resources.UserLogin import UserLogin, UsersList, UserLogout, UserById, Cars, CarsById

V1_URL = '/v1/api'

application = Flask(__name__)
api = Api(application)

api.add_resource(Hello, V1_URL + '/', endpoint='hello-api')
api.add_resource(Hello, '/', endpoint='hello-root')
api.add_resource(UserById, V1_URL + '/users/<int:id>')
api.add_resource(UserLogin, V1_URL + '/users/login')
api.add_resource(UserLogout, V1_URL + '/users/logout')
api.add_resource(UsersList, V1_URL + '/users')
#api.add_resource(DriversList, V1_URL + '/users/drivers')

api.add_resource(GreetAdd, '/greet')
api.add_resource(GoodBye, '/goodbye')

if __name__ == "__main__":
    application.run(host='localhost')

