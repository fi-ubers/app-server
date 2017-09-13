import json

from src.main.resources import SimpleAPI as testAPI
from src.main.myApp import application as app

class TestMyApp(object):
    def test_hello(self):
        h = testAPI.Hello()
        assert h.get() == "Hello"

    def test_goodbye_get(self):
        g = testAPI.GoodBye()
        assert g.get() == "Good Bye"

    def test_goodbye_post(self):
        g = testAPI.GoodBye()
        assert g.post() == {'good':'bye'}


class UserCollectionMock(object):
    def __init__(self):
        self.users = [ { "_id" : 1, "name" : "Juan" } ]

    def find(self):
        return self.users

    def insert_one(self, new):
        self.users.append(new)

    def delete_many(self, cond):
        for key in cond.keys():
            for user in self.users:
                if (user.has_key(key) or user[key] == cond[key]):
                    self.users.remove(user)


class TestSimpleAPI(object):
    def test_users(self):
        # Setting up fake users list
        testAPI.users = UserCollectionMock()

        print(testAPI.users.find())
        expected = { "users" : testAPI.users.find() }

        self.app = app.test_client()
        response = self.app.get('/greet')

        response_parsed = json.loads(response.get_data())
        assert (response_parsed == expected and response.status_code == 200)


    def test_insert_success(self):
        testAPI.users = UserCollectionMock()

        new_user = { "id" : 2, "name" : "Ale" }
        expected = { "user" : { "_id" : 2, "name" : "Ale" } }

        self.app = app.test_client()
        response = self.app.post('/greet', data = json.dumps({ "user" : new_user }),
                                content_type = 'application/json')

        response_parsed = json.loads(response.get_data())
        assert (response_parsed == expected and response.status_code == 201)


    def test_insert_duplicate(self):
        testAPI.users = UserCollectionMock()

        new_user = [{ "id" : 1, "name" : "Ale" }]

        expected = { "message" : "user id already exists" }

        self.app = app.test_client()
        response = self.app.post('/greet', data = json.dumps({ "user" : new_user[0] }),
                                content_type = 'application/json')

        response_parsed = json.loads(response.get_data())
        assert (response_parsed == expected and response.status_code == 400)


    def test_get_nonexistent_user(self):
        testAPI.users = UserCollectionMock()

        self.app = app.test_client()
        response = self.app.get('/greet/2')

        assert (response.status_code == 404)


    def test_post_missing_id(self):
        testAPI.users = UserCollectionMock()

        new_user = [{ "name" : "Ale" }]

        expected = { "message" : "request missing id" }

        self.app = app.test_client()
        response = self.app.post('/greet', data = json.dumps({ "user" : new_user[0] }),
                                content_type = 'application/json')

        response_parsed = json.loads(response.get_data())
        assert (response_parsed == expected and response.status_code == 400)


    def test_remove_success(self):
        testAPI.users = UserCollectionMock()

        fake_users = [{ "_id" : 1, "name" : "Juan" }]
        expected = { "user" : fake_users[0] }

        self.app = app.test_client()
        response = self.app.delete('/greet/1')

        response_parsed = json.loads(response.get_data())
        assert (response_parsed == expected and response.status_code == 200)

    def test_delete_invalid(self):
        testAPI.users = UserCollectionMock()

        self.app = app.test_client()
        response = self.app.delete('/greet/2')

        assert (response.status_code == 404)
