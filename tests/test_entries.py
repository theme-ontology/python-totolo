import pytest

from totolo.impl.entry import TOEntry
from totolo.story import TOStory
from totolo.theme import TOTheme

STORY_DATA = {
    "Title": "foo title",
    "Description": "foo description" * 200,
    "Authors": "foo authors",
    "Variation": "foo variation",
    "References": ["ref1", "http://ref2"],
    "Ratings": ["foo <5>", "bar", "3"],
    "Collections": ["Collection: foo", "garbage"],
    "Component Stories": ["foo", "bar"],
    "Related Stories": ["foo"],
    "Choice Themes": [],
    "Major Themes": [],
    "Minor Themes": [],
    "Not Themes": [],
    "Other Keywords": [],
}

THEME_DATA = {
    "Description": "foo description" * 200,
    "Parents": ["foo", "bar"],
    "Notes": "foo notes",
    "Examples": "foo example",
    "References": ["ref1", "http://ref2"],
    "Aliases": ["bar alias"],
}


def check_descriptions(descriptions, has_description=True,
                       has_references=True):
    desc1, desc2, desc3 = descriptions
    assert isinstance(desc1, str)
    assert isinstance(desc2, str)
    assert isinstance(desc3, str)

    if has_description:
        for desc in descriptions:
            assert "foo description" in desc
    if has_references:
        assert "ref1" in desc1
        assert "ref2" in desc1
    else:
        assert "References:" not in desc1

    assert desc2.startswith('<P class="obj-description">')
    assert desc2.strip().endswith('</P>')

    assert len(desc3) < 300


class TestTOEntry:
    def test_oddities(self):
        entry = TOEntry(name="foo", source="""
:: Entry Name
foo
:: junkline
:: a very long junkline
bar
        """)
        assert len(str(entry)) > 3
        warnings = list(entry.validate())
        assert len(warnings) == 1
        assert "junk in entry" in warnings[0]
        assert list(entry.ancestors()) == ["foo"]
        assert list(entry.descendants()) == ["foo"]
        with pytest.raises(KeyError):
            del entry["foo"]


class TestTOStory:
    def test_story_order(self):
        objects = [
            TOStory(name="bar"),
            TOStory(name="foo"),
            TOStory(name="baz"),
        ]
        names = ["bar", "baz", "foo"]
        assert [obj.name for obj in sorted(objects)] == names
        assert len(set(objects)) == 3
        assert set({obj.name: obj for obj in objects}.keys()) == set(names)

    def test_story_include_single_attribute(self):
        for key1 in STORY_DATA:
            story = TOStory(name="foo")
            for key2 in STORY_DATA:
                if story.field_required(key2) or key1 == key2:
                    story[key2] = STORY_DATA[key2]
            descriptions = [
                story.verbose_description(),
                story.html_description(),
                story.html_short_description(),
            ]
            check_descriptions(
                descriptions,
                key1 == "Description",
                key1 == "References",
            )

    def test_story_exclude_single_attribute(self):
        for key1 in STORY_DATA:
            story = TOStory(name="foo")
            for key2 in STORY_DATA:
                if story.field_required(key2) or key1 != key2:
                    story[key2] = STORY_DATA[key2]
            descriptions = [
                story.verbose_description(),
                story.html_description(),
                story.html_short_description(),
            ]
            check_descriptions(
                descriptions,
                key1 != "Description",
                key1 != "References",
            )

    def test_story_properties(self):
        story = TOStory(name="foo")
        assert story.sid == "foo"

        story["Date"] = "gobbledygook"
        assert story.year == 0
        story["Date"] = "81 BC"
        assert story.year == -81
        story["Date"] = "1981-04-15"
        assert story.year == 1981
        story["Date"] = "1981 Apr 15  "
        assert story.year == 1981
        assert story.date == "1981 Apr 15"

        story["Title"] = " foo foo  "
        assert story.title == "foo foo"

        story["Authors"] = "mikael"
        assert str(story["Authors"]) == "mikael"
        del story["Authors"]
        assert str(story["Authors"]) == ""

        with pytest.raises(RuntimeError):
            list(story.iter_themes())


class TestTOTheme:
    def test_theme_order(self):
        objects = [
            TOTheme(name="bar"),
            TOTheme(name="foo"),
            TOTheme(name="baz"),
        ]
        names = ["bar", "baz", "foo"]
        assert [obj.name for obj in sorted(objects)] == names
        assert len(set(objects)) == 3
        assert set({obj.name: obj for obj in objects}.keys()) == set(names)

    def test_theme_include_single_attribute(self):
        for key1 in THEME_DATA:
            theme = TOTheme(name="bar")
            for key2 in THEME_DATA:
                if theme.field_required(key2) or key1 == key2:
                    theme[key2] = THEME_DATA[key2]
            descriptions = [
                theme.verbose_description(),
                theme.html_description(),
                theme.html_short_description(),
            ]
            check_descriptions(
                descriptions,
                key1 == "Description",
                key1 == "References",
            )

    def test_theme_exclude_single_attribute(self):
        for key1 in THEME_DATA:
            theme = TOTheme(name="foo")
            for key2 in THEME_DATA:
                if theme.field_required(key2) or key1 != key2:
                    theme[key2] = THEME_DATA[key2]
            descriptions = [
                theme.verbose_description(),
                theme.html_description(),
                theme.html_short_description(),
            ]
            check_descriptions(
                descriptions,
                key1 != "Description",
                key1 != "References",
            )

    def test_theme_properties(self):
        theme = TOTheme(name="foo")
        assert theme.name == "foo"

        theme["Notes"] = "foo"
        assert str(theme["Notes"]) == "foo"
        del theme["Notes"]
        assert str(theme["Notes"]) == ""
