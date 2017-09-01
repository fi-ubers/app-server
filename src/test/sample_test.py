from ..main.resources.SimpleAPI import Hello, GoodBye

class TestMyApp(object):
    def test_hello(self):
        h = Hello()
        assert h.get() == "Hello"

    def test_goodbye_get(self):
        g = GoodBye()
        assert g.get() == "Good Bye"

    def test_goodbye_post(self):
        g = GoodBye()
        assert g.post() == {'good':'bye'}
