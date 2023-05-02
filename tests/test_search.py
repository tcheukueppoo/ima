import pytest

from ima.search import Search

class test_search():
    def __init__(self):
        s = Search()

    def test_next_back(self, engine, query):
        s.set_engine(engine)
        s.set_query(query)

        r1 = s.next()
        r2 = s.next()
        r3 = s.next()
        b2 = s.back()
        b1 = s.back()

        assert r1 == b1
        assert r2 == b2

        f2 = s.next()
        f3 = s.next()

        assert f2 == r2
        assert f3 == r3


test_object = test_search()
test_object.test_next_back('google', 'What is wikipedia')
'''
test_object.test_next_back('duckduckgo', 'What is wikipedia')
test_object.test_next_back('yahoo', 'What is wikipedia')

test_object.test_next_back('google', 'Meaning of life')
test_object.test_next_back('duckduckgo', 'Meaning of love')
test_object.test_next_back('yahoo', 'How to be a rich man?')
'''
