from flask import Flask
from flask_restful import Resource, Api

from resources.SimpleAPI import Hello, GoodBye

application = Flask(__name__)
api = Api(application)

api.add_resource(Hello, '/')
api.add_resource(GoodBye, '/goodbye')


if __name__ == "__main__":
    application.run(host='localhost')

