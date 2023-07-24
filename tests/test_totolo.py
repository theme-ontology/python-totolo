import difflib
import os.path
import tempfile

import pandas as pd

import totolo


def filediff(path1, path2):
    with open(path1) as file1, open(path2) as file2:
        for line in difflib.unified_diff(
                file1.readlines(), file2.readlines(), n=0, lineterm=""):
            yield line


def set_pandas_display_options() -> None:
    display = pd.options.display
    display.max_columns = 100
    display.max_rows = 1000
    display.max_colwidth = 90
    display.width = 200


class TestIO:
    def test_empty(self):
        to = totolo.empty()
        assert len(to) == 0

    def test_remote_version_old(self):
        to = totolo.remote.version("v0.3.3")
        to.print_warnings()
        assert len(to) > 3

    def test_remote_version_new(self):
        to = totolo.remote.version("v2023.06")
        to.print_warnings()
        assert len(to) > 3

    def test_theme_attributes(self):
        to = totolo.files("tests/data/to-2023.07.09.th.txt")
        t = to.theme["coping with senility"]
        t.print()
        assert t.name == "coping with senility"
        assert t["Description"].str().startswith(
            "A character copes with a loss of their mental faculties")
        assert t["Parents"].list() == ["human health condition"]
        assert t["Notes"].str().startswith(
            "This theme is used for example when")
        assert t["Examples"].str().startswith(
            'In tng3x23 "Sarek", Sarek coped')
        assert t["References"].list() == ["https://en.wikipedia.org/wiki/Dementia"]
        assert t["Aliases"].list() == ["coping with dementia"]

    def test_story_attributes(self):
        name = "play: The Taming of the Shrew (1592)"
        to = totolo.files("tests/data/to-sample-2023.07.09.st.txt")
        s = to.story[name]
        s.print()
        assert s.name == name
        assert s.sid == name
        assert s["Title"].str() == "The Taming of the Shrew"
        assert s["Date"].str() == "1592"
        assert s.date == "1592"
        assert s.year == 1592
        assert "a drunken tinker named Christopher Sly" in s["Description"].str()
        assert s["Authors"].str() == "William Shakespeare"
        assert s["References"].list() == [
            "https://en.wikipedia.org/wiki/The_Taming_of_the_Shrew"
        ]
        assert s["Ratings"].list() == ["4 <mikael>"]
        assert s["Collections"].list() == []

    def test_fetch_and_write(self):
        print("Downloading master...")
        to1 = totolo.remote()
        with tempfile.TemporaryDirectory() as prefix:
            print(f"Writing to: {prefix}")
            to1.write(prefix=prefix, verbose=True)
            print(f"Reading from: {prefix}")
            to2 = totolo.files(prefix)
            assert len(to1) == len(to2)
            assert len(to1.theme) == len(to2.theme)
            assert len(to1.story) == len(to2.story)

    def test_write_integrity(self):
        prefix1 = "tests/data/sample-2023.07.23"
        filenames = [
            "notes/stories/film/film-scifi-1920s.st.txt",
            "notes/themes/primary.th.txt",
        ]
        to1 = totolo.files(prefix1)
        with tempfile.TemporaryDirectory() as prefix2:
            print(f"Writing to: {prefix2}")
            to1.write(prefix=prefix2, verbose=True)
            print(f"Reading from: {prefix2}")
            to2 = totolo.files(prefix2)
            assert len(to1) == len(to2)
            assert len(to1.theme) == len(to2.theme)
            assert len(to1.story) == len(to2.story)
            for suffix in filenames:
                print(f"Comparing: {suffix}")
                path1 = os.path.join(prefix1, suffix)
                path2 = os.path.join(prefix2, suffix)
                lines = list(filediff(path1, path2))
                for line in lines:
                    print(line, end="")
                assert (len(lines) == 0)


class TestFeatures:
    def test_theme_ancestors(self):
        to = totolo.files("tests/data/to-2023.07.09.th.txt")
        themes = list(to.theme["love"].ancestors())
        assert set(themes) == set([
            'love',
            'human emotion',
            'individual humans',
            'personal human experience',
            'the human world',
        ])

    def test_theme_descendants(self):
        to = totolo.files("tests/data/to-2023.07.09.th.txt")
        themes = list(to.theme["love"].descendants())
        assert set(themes) == set([
            'love',
            'romantic love',
            'love kindled by danger',
            'impossible love',
            'love at first sight',
            'infatuation',
            'obsessive love',
            'first crush',
            'epic love',
            'forbidden love',
            'secret crush',
            'old-age love',
            'unrequited love',
            'nostalgic love',
            'tragic love',
            'romantic jealousy',
            'familial love',
            'love of a pet',
            'platonic love',
            'sororal love',
            'parental love',
            'paternal love',
            'maternal love',
            'matrimonial love',
            'filial love',
        ])

    def test_story_ancestors(self):
        to = totolo.files("tests/data/storytree.st.txt")
        stories = list(to.story["Collection: B2"].ancestors())
        assert set(stories) == set(
            ['Collection: B2', 'Collection: A', 'Collection: B1'])

    def test_story_descendants(self):
        to = totolo.files("tests/data/storytree.st.txt")
        stories = list(to.story["Collection: B2"].descendants())
        assert set(stories) == set(['Collection: B2', 'story: C'])

    def test_dataframe(self):
        to = totolo.files("tests/data/sample-2023.07.23")
        df = to.dataframe()
        set_pandas_display_options()
        themed_stories = len(
            [name for name in to.story if not name.startswith("Collection")])
        story_themes = sum(len(list(s.iter_theme_entries())) for s in to.story.values())
        set_pandas_display_options()
        print()
        print(df[:50])
        assert len(df) == story_themes
        assert df["story_id"].nunique() == themed_stories


class TestValidation:
    def test_cycle_warning(self):
        to = totolo.files("tests/data/cycles1.th.txt")
        assert len([msg for msg in to.validate_cycles() if "Cycle:" in msg]) == 1
        to = totolo.files("tests/data/cycles2.th.txt")
        assert len([msg for msg in to.validate_cycles() if "Cycle:" in msg]) == 1
        to = totolo.files("tests/data/cycles3.th.txt")
        assert len([msg for msg in to.validate_cycles() if "Cycle:" in msg]) == 1
