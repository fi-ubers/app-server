import json

from ..main.resources import SimpleAPI as testAPI
from ..main.myApp import application as app

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


class TestSimpleAPI(object):
    def test_users(self):
        # Setting up fake users list
        fake_users = [{ "id" : 1, "name" : "Juan" }]
        expected = { "users" : fake_users }

        testAPI.users = fake_users 

        self.app = app.test_client()
        response = self.app.get('/greet')

        response_parsed = json.loads(response.get_data())
        assert (response_parsed == expected and response.status_code == 200)


    def test_insert_success(self):
        fake_users = [{ "id" : 1, "name" : "Juan" }]
        new_user = [{ "id" : 2, "name" : "Ale" }]
        expected = { "user" : new_user[0] }

        testAPI.users = fake_users 

        self.app = app.test_client()
        response = self.app.post('/greet', data = json.dumps({ "user" : new_user[0] }),
                                content_type = 'application/json')

        response_parsed = json.loads(response.get_data())
        assert (response_parsed == expected and response.status_code == 201)


    def test_insert_duplicate(self):
        fake_users = [{ "id" : 1, "name" : "Juan" }]
        new_user = [{ "id" : 1, "name" : "Ale" }]

        expected = { "message" : "user id already exists" }

        testAPI.users = fake_users 

        self.app = app.test_client()
        response = self.app.post('/greet', data = json.dumps({ "user" : new_user[0] }),
                                content_type = 'application/json')

        response_parsed = json.loads(response.get_data())
        assert (response_parsed == expected and response.status_code == 400)


    def test_get_nonexistent_user(self):
        fake_users = [{ "id" : 1, "name" : "Juan" }]

        testAPI.users = fake_users 

        self.app = app.test_client()
        response = self.app.get('/greet/2')

        assert (response.status_code == 404)


    def test_post_missing_id(self):
        fake_users = [{ "id" : 1, "name" : "Juan" }]
        new_user = [{ "name" : "Ale" }]

        expected = { "message" : "request missing id" }

        testAPI.users = fake_users 

        self.app = app.test_client()
        response = self.app.post('/greet', data = json.dumps({ "user" : new_user[0] }),
                                content_type = 'application/json')

        response_parsed = json.loads(response.get_data())
        assert (response_parsed == expected and response.status_code == 400)


    def test_remove_success(self):
        fake_users = [{ "id" : 1, "name" : "Juan" }]
        expected = { "user" : fake_users[0] }

        testAPI.users = fake_users 

        self.app = app.test_client()
        response = self.app.delete('/greet', data = json.dumps({ "id" : 1 }),
                                content_type = 'application/json')

        response_parsed = json.loads(response.get_data())
        assert (response_parsed == expected and response.status_code == 200)


    def test_delete_nonexistent_user(self):
        fake_users = [{ "id" : 1, "name" : "Juan" }]

        testAPI.users = fake_users 

        self.app = app.test_client()
        response = self.app.delete('/greet', data = json.dumps({ "id" : 2 }),
                                content_type = 'application/json')

        assert (response.status_code == 404)
