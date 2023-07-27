import pytest

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


class TestTOEntries:
    def check_descriptions(self, descriptions, has_description=True,
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
            self.check_descriptions(
                descriptions,
                key1 == "Description",
                key1 == "References",
            )

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
            self.check_descriptions(
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
            self.check_descriptions(
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

        with pytest.raises(RuntimeError):
            list(story.iter_themes())
