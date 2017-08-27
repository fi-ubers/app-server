from ..main import myApp

class TestMyApp(object):
    def test_hello(self):
        h = myApp.Hello()
        assert h.get() == "Hello"

    def test_goodbye_get(self):
        g = myApp.GoodBye()
        assert g.get() == "Good Bye"

    def test_goodbye_post(self):
        g = myApp.GoodBye()
        assert g.post() == {'good':'bye'}
