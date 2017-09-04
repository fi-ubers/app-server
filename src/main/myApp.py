from flask import Flask
from flask_restful import Resource, Api
from src.main.log.Logger import Log

application = Flask(__name__)
api = Api(application)

class Hello(Resource):
    @Log("GET returns Hello")
    def get(self):
        print("GET at /")
        return 'Hello' 

class GoodBye(Resource):
    @Log("GET returns Good Bye")
    def get(self):
        print("GET at /goodbye")
        return 'Good Bye'

    def post(self):
        print("POST at /goodbye")
        return {'good':'bye'}

api.add_resource(Hello, '/')
api.add_resource(GoodBye, '/goodbye')

#@application.route("/")
#def hello():
#    return "<h1 style='color:blue'>Hello there!</h1>"

if __name__ == "__main__":
    application.run(host='localhost')

