from totolo.impl.core import TOObject, sa


class TOTest(TOObject):
    b = sa("txt", default="foo, bar: b", required=True)
    c = sa("txt", default="foo, bar: c", required=True)
    a = sa("txt", default="foo, bar: a", required=True)


class TestAPI:
    def test_object(self):
        a = TOTest(q=2, b="monkey")
        assert a.a == "foo, bar: a"
        assert a.b == "monkey"
        assert a.q == 2
