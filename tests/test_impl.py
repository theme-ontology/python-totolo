import pytest

import totolo
from totolo.impl.core import TOObject, a, sa
from totolo.impl.field import TOField
from totolo.impl.parser import TOParser


class TOTest1(TOObject):
    a1 = a("foo")
    a2 = a("bar")
    a3 = a(private=True)
    bb = sa("txt", default="baz: b", required=True)
    cc = sa("txt", default="baz: c")
    aa = sa("txt", default="baz: a")


class TestTOObject:
    def test_object_attributes(self):
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


class TestField:
    def make_field(self, fieldtype="text"):
        field = TOField(name="foo", fieldtype=fieldtype)
        field.data.append("data line")
        field.source.append("source line")
        if fieldtype == "kwlist":
            field.insert_kw(
                keyword="foo",
                motivation="bar",
                capacity="baz",
                notes="widget",
            )
        else:
            field.parts.append("foo bar")
        return field

    def test_create(self):
        fieldtypes = ["text", "list", "kwlist", "blob", "unknown"]
        for fieldtype in fieldtypes:
            field = self.make_field(fieldtypes)
            assert "foo" in str(field)

    def test_edit_keywords(self):
        field = self.make_field("kwlist")
        assert str(field.parts[0]) == "foo <baz> [bar] {widget}"
        field.update_kw(
            "foo",
            keyword="foo2",
            motivation="bar2",
            capacity="baz2",
            notes="widget2",
        )
        assert str(field.parts[0]) == "foo2 <baz2> [bar2] {widget2}"
        field.insert_kw(keyword="apa")
        field.insert_kw(keyword="bepa")
        field.insert_kw(keyword="apa")
        count = field.delete_kw("apa")
        assert count == 2
        assert len(field.parts) == 2
        count = field.delete_kw("apa")
        assert count == 0
        assert len(field.parts) == 2
        count = field.delete_kw("bepa")
        count = field.delete_kw("foo2")
        assert count == 1
        assert len(field.parts) == 0


class TestTOParser:
    def test_oddities(self):
        to = totolo.empty()

        with pytest.raises(ValueError):
            TOParser.add_url(to, "gobbledygook")

        with pytest.raises(AssertionError):
            list(TOParser.iter_kwitems(["malformed ] field"]))
        with pytest.raises(AssertionError):
            list(TOParser.iter_kwitems(["malformed <[]} field"]))
        with pytest.raises(AssertionError):
            list(TOParser.iter_kwitems(["malformed {}> field"]))
        with pytest.raises(AssertionError):
            list(TOParser.iter_kwitems(["malformed <<>> field"]))
        with pytest.raises(AssertionError):
            list(TOParser.iter_kwitems(["malformed {{}} field"]))
        with pytest.raises(AssertionError):
            list(TOParser.iter_kwitems(["malformed [[]] field"]))
