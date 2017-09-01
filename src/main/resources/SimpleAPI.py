from flask_restful import Resource

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


