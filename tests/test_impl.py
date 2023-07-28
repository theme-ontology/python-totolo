import pytest

import totolo
from totolo.impl.core import TOObject, a, sa
from totolo.impl.field import TOField
from totolo.impl.parser import TOParser
from totolo.story import TOStory


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

    def test_representation(self):
        obj = TOObject()
        strs = [str(obj), repr(obj)]
        assert all(isinstance(x, str) for x in strs)
        assert all(len(x) > 5 for x in strs)

    def test_field_lookup(self):
        obj = TOTest1()
        assert obj.field_required("bb") == True
        assert obj.field_required("cc") == False
        assert obj.field_required("qq") == False
        assert obj.field_type("bb") == "txt"
        assert obj.field_type("qq") == "unknown"

    def test_typedef(self):
        strs = [
            str(TOTest1._to_attrs["a1"]),
            str(TOTest1._to_attrs["bb"]),
            repr(TOTest1._to_attrs["a1"]),
            repr(TOTest1._to_attrs["bb"]),
        ]
        for strobj in strs:
            assert isinstance(strobj, str)
            assert len(strobj) > 5


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
            field = self.make_field(fieldtype)
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

    def test_freeze(self):
        field = self.make_field("kwlist").freeze()
        with pytest.raises(AttributeError):
            field.data = [1]
        with pytest.raises(AttributeError):
            field.delete_kw("foo")
        with pytest.raises(AttributeError):
            field.update_kw("foo")
        with pytest.raises(AttributeError):
            field.insert_kw(0, keyword="foo")

    def test_representation(self):
        field = self.make_field("kwlist").freeze()
        strs = [str(field), repr(field)]
        assert all(isinstance(x, str) for x in strs)
        assert all(len(x) > 5 for x in strs)


class TestTOParser:
    def test_empty_lines(self):
        ontology = totolo.files("tests/data/messy.st.txt")
        print(ontology)
        title_field = ontology.story["story: C"]["Title"]
        date_field = ontology.story["story: C"]["Date"]
        assert title_field.source[-2] == ""
        assert date_field.source[-2] == ""
        date_field.str() == "1920-2017"
        title_field.str() == "C"

    def test_field(self):
        field = TOParser.make_field([
            ":: Date", "1789", "", "",
        ], fieldtype="date")
        assert field.source[-1] == ""
        assert field.source[-2] == ""

    def test_entry(self):
        story = TOParser.populate_entry(TOStory(), [
            "a story",
            "=======",
            "",
            ":: Date",
            "1789",
            "",
            "",
        ])
        assert story.source[-1] == ""
        assert story.source[-2] == ""
        assert story.source[-3] == "1789"

    def test_oddities(self):
        ontology = totolo.empty()

        with pytest.raises(ValueError):
            TOParser.add_url(ontology, "gobbledygook")

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
