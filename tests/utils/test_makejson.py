import sys
from unittest.mock import patch
import json
import urllib
import io

import totolo
import totolo.util.makejson

from tests.test_totolo import precache_remote_resources


def validate1(capsys):
    out, err = capsys.readouterr()
    dd = json.loads(out)
    expected = {
        "lto": 8,
        "themes": 2940,
        "stories": 45,
        "collections": 57,
    }
    assert len(dd) == 4
    for key, val in dd.items():
        assert len(val) == expected[key]


class TestMakeJson:
    def test_helpers(self):
        assert totolo.util.makejson.include_story({}) == False
        assert totolo.util.makejson.include_theme({}) == False
        assert totolo.util.makejson.include_story({"major themes": []}) == False
        assert totolo.util.makejson.include_story({"major themes": ["foo"]}) == True
        dd = totolo.util.makejson.convert_story({
            "name": "foo",
            "major themes": [{"1":"1"}, {"2":"2"}],
            "minor themes": [{"3":"3"}, {"4":"4"}],
        })
        assert len(dd["themes"]) == 4

    def test_from_path(self, capsys):
        p1 = "tests/data/sample-2023.07.23/notes"
        testargs = ["makejson", "--path", p1]
        with patch.object(sys, 'argv', testargs):
            totolo.util.makejson.main()
        validate1(capsys)

    def test_from_path_narg(self, capsys):
        p1 = "tests/data/sample-2023.07.23/notes"
        testargs = ["makejson", p1]
        with patch.object(sys, 'argv', testargs):
            totolo.util.makejson.main()
        validate1(capsys)

    def test_bad_usage(self, capsys):
        testargs = ["makejson", "--path", "foo", "--version", "foo"]
        with patch.object(sys, 'argv', testargs):
            totolo.util.makejson.main()
        out, err = capsys.readouterr()
        assert all(x in err for x in ["--path", "--version", "positional"])
        assert not out

    def test_remote_version(self, capsys):
        precache_remote_resources()
        testargs = ["makejson", "--version", "v2023.06"]
        with patch.object(sys, 'argv', testargs):
            with open("tests/data/sample-2023.07.23.tar.gz", "rb+") as fh:
                with patch.object(urllib.request, 'urlopen', return_value=fh):
                    totolo.util.makejson.main()
        validate1(capsys)

    def test_remote_version_narg(self, capsys):
        precache_remote_resources()
        testargs = ["makejson", "v2023.06"]
        with patch.object(sys, 'argv', testargs):
            with open("tests/data/sample-2023.07.23.tar.gz", "rb+") as fh:
                with patch.object(urllib.request, 'urlopen', return_value=fh):
                    totolo.util.makejson.main()
        validate1(capsys)

    def test_remote_head(self, capsys):
        precache_remote_resources()
        testargs = ["makejson"]
        with patch.object(sys, 'argv', testargs):
            with open("tests/data/sample-2023.07.23.tar.gz", "rb+") as fh:
                with patch.object(urllib.request, 'urlopen', return_value=fh):
                    totolo.util.makejson.main()
        validate1(capsys)

    def test_component_parameters(self, capsys):
        p1 = "tests/data/sample-2023.07.23/notes"
        component_keys = ["themes", "stories", "collections"]
        for key in component_keys:
            testargs = ["makejson", "--path", p1, f"-{key[0]}"]
            with patch.object(sys, 'argv', testargs):
                totolo.util.makejson.main()
            out, _err = capsys.readouterr()
            dd = json.loads(out)
            assert key in dd
            for key2 in component_keys:
                if key2 != key:
                    assert key2 not in dd

    def test_verbosity_official(self, capsys):
        p1 = "tests/data/sample-2023.07.23/notes"
        testargs = ["makejson", p1, "--verbosity", "official"]
        with patch.object(sys, 'argv', testargs):
            totolo.util.makejson.main()
        out, _err = capsys.readouterr()
        dd = json.loads(out)
        assert "source" not in dd["stories"][0]
        assert "ratings" not in dd["stories"][0]

        testargs = ["makejson", "--verbosity", "all"]
        with patch.object(sys, 'argv', testargs):
            totolo.util.makejson.main()
        out, _err = capsys.readouterr()
        dd = json.loads(out)
        assert "source" in dd["stories"][0]
        assert "ratings" in dd["stories"][0]

    def test_verbosity_all(self, capsys):
        p1 = "tests/data/sample-2023.07.23/notes"
        testargs = ["makejson", p1, "--verbosity", "all"]
        with patch.object(sys, 'argv', testargs):
            totolo.util.makejson.main()
        out, _err = capsys.readouterr()
        dd = json.loads(out)
        assert "source" in dd["stories"][0]
        assert "ratings" in dd["stories"][0]

    def test_reorg_default(self, capsys):
        p1 = "tests/data/collection-reorg.st.txt"
        testargs = ["makejson", p1]
        with patch.object(sys, 'argv', testargs):
            totolo.util.makejson.main()
        out, _err = capsys.readouterr()
        dd = json.loads(out)
        for story_dict in dd["stories"]:
            assert "collections" not in story_dict
        assert dd["collections"][0]["component stories"] == ["story: B"]
        assert dd["collections"][1]["component stories"] == ["story: A", "story: B"]

    def test_no_reorg(self, capsys):
        p1 = "tests/data/collection-reorg.st.txt"
        testargs = ["makejson", p1, "--no-reorg"]
        with patch.object(sys, 'argv', testargs):
            totolo.util.makejson.main()
        out, _err = capsys.readouterr()
        dd = json.loads(out)
        for story_dict in dd["stories"]:
            assert "collections" in story_dict
        for collection_dict in dd["collections"]:
            assert "collections" not in collection_dict
