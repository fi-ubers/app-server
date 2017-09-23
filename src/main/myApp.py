from flask import Flask
from flask_restful import Resource, Api

from src.main.mongodb.MongoHandler import MongoHandler
appdb = MongoHandler()

from src.main.resources.SimpleAPI import Hello, GoodBye, Greet, GreetAdd

application = Flask(__name__)
api = Api(application)

api.add_resource(Hello, '/')
api.add_resource(GoodBye, '/goodbye')
api.add_resource(Greet, '/greet/<int:id>')
api.add_resource(GreetAdd, '/greet')

if __name__ == "__main__":
    application.run(host='localhost')

