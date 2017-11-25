from flask import Flask
from flask_restful import Resource, Api

import src.main.mongodb.MongoController
from src.main.resources.UserLogin import UserLogin, UsersList, UserLogout, UserById, LocUserById
from src.main.resources.UserCars import Cars, CarsById
from src.main.resources.UserTransactions import UserTransactions
from src.main.resources.Trips import UserTrips, Trips, TripEstimation, TripsById
from src.main.resources.TripAction import TripActions
from src.main.resources.Paymethods import Paymethods
from src.main.resources.Directions import Directions

V1_URL = '/v1/api'

application = Flask(__name__)
api = Api(application)

#User operations
api.add_resource(LocUserById, V1_URL + '/users/<int:id>/location')
api.add_resource(UserById, V1_URL + '/users/<int:id>')
api.add_resource(UserLogin, V1_URL + '/users/login')
api.add_resource(UserLogout, V1_URL + '/users/logout')
api.add_resource(UsersList, V1_URL + '/users')

# Car operations
api.add_resource(Cars, V1_URL + '/users/<int:id>/cars')
api.add_resource(CarsById, V1_URL + '/users/<int:userId>/cars/<int:carId>')

# Transaction operations
api.add_resource(UserTransactions, V1_URL + '/users/<int:id>/transactions')

# Trips operations
api.add_resource(Trips, V1_URL + '/trips')
api.add_resource(TripsById, V1_URL + '/trips/<string:id>')
api.add_resource(TripActions, V1_URL + '/trips/<string:id>/action')


###### CHECK THESE
api.add_resource(UserTrips, V1_URL + '/users/<int:id>/trips')
api.add_resource(TripEstimation, V1_URL + '/trips/estimation')

# Payment operations
api.add_resource(Paymethods, V1_URL + '/payment')

# Google API
api.add_resource(Directions, V1_URL + '/directions')

#if __name__ == "__main__":
#    application.run(host='localhost')
