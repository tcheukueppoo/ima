import pytest

from ima.search import Search

s = Search()

def next_back(s):
    r1 = s.next()
    r2 = s.next()
    r3 = s.next()
    b2 = s.back()
    b1 = s.back()

    assert r1 == b1
    assert r2 == b2

    f2 = s.next()
    assert f2 == r2

    f3 = s.next()
    assert r3 == f3

def test_next_back_google():
    s.set_engine('google')
    s.set_query('What is wikipedia')
    next_back(s)


def test_next_back_duckduckgo():
    s.set_engine('duckduckgo')
    s.set_query('What is wikipedia')
    next_back(s)

'''
test_object.test_next_back('duckduckgo', 'What is wikipedia')
test_object.test_next_back('yahoo', 'What is wikipedia')

test_object.test_next_back('google', 'Meaning of life')
test_object.test_next_back('duckduckgo', 'Meaning of love')
test_object.test_next_back('yahoo', 'How to be a rich man?')
'''
