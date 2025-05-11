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

    def test_bad_usage(self, capsys):
        testargs = ["makejson", "--path", "foo", "--version", "foo"]
        with patch.object(sys, 'argv', testargs):
            totolo.util.makejson.main()
        out, err = capsys.readouterr()
        assert "--path and --version" in out
        assert not err

    def test_remote_version(self, capsys):
        precache_remote_resources()
        testargs = ["makejson", "--version", "v2023.06"]
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

    def test_parameters(self, capsys):
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
