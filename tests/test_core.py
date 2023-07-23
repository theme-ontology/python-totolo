from totolo.impl.core import TOObject, a, sa


class TOTest1(TOObject):
    a1 = a("foo")
    a2 = a("bar")
    a3 = a(private=True)
    bb = sa("txt", default="baz: b", required=True)
    cc = sa("txt", default="baz: c")
    aa = sa("txt", default="baz: a")


class TOTest2(TOObject):
    foo_Bar = a()
    Bar_Baz = a(private=True)
    Baz_bar = sa()


class TestAPI:
    def test_object_attrbiutes(self):
        a = TOTest1(qq=2, bb="monkey", a2="fox")
        assert a.a1 == "foo"
        assert a.a2 == "fox"
        assert a.bb == "monkey"
        attrs = [k for k, _ in a.iter_attrs()]
        sattrs = [k for k, _ in a.iter_stored()]
        assert attrs == ["a1", "a2", "a3", "bb", "cc", "aa"]
        assert sattrs == ["bb", "cc", "aa"]
        assert not hasattr(a, "aa")
        assert not hasattr(a, "cc")
        assert not hasattr(a, "a3")

    def test_underscore(self):
        obj = TOTest2()
        assert [k for k, _ in obj.iter_attrs()] == ["foo_Bar", "Bar_Baz", "Baz bar"]
        assert [k for k, _ in obj.iter_stored()] == ["Baz bar"]
