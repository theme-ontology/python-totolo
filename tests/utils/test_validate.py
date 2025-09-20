import sys
from unittest.mock import patch
import urllib

import totolo
import totolo.util.validate

from tests.test_totolo import precache_remote_resources


EXPECTED_WARNINGS_20230723 = """
tests/data/sample-2023.07.23/notes/stories/film/film-scifi-1920s.st.txt: In movie: The Hands of Orlac (1924): Missing '{' in: ['body part transplant ', 'hand', '', '']
tests/data/sample-2023.07.23/notes/stories/film/film-scifi-1930s.st.txt: In movie: The Walking Dead (1936): Missing '{' in: ['artificial body part ', 'heart', '', '']
tests/data/sample-2023.07.23/notes/stories/film/film-scifi-1930s.st.txt: In movie: The Man They Could Not Hang (1939): Missing '{' in: ['artificial body part ', 'heart', '', '']
tests/data/sample-2023.07.23/notes/stories/film/film-scifi-1930s.st.txt: In movie: The Return of Doctor X (1939): Missing '{' in: ['artificial body part ', 'blood', '', '']
tests/data/sample-2023.07.23/notes/themes/primary.th.txt: artificial body part: unknown field 'Template'
tests/data/sample-2023.07.23/notes/themes/primary.th.txt: historical figure: unknown field 'Template'
movie: Algol: Tragedy of Power (1920): Undefined 'major theme' with name 'the lust for gold'
movie: Woman in the Moon (1929): Undefined 'minor theme' with name 'the lust for gold'
""".strip()


def validate1(capsys, expected = None):
    out, err = capsys.readouterr()
    assert all(line.startswith("::") for line in err.strip().splitlines())
    assert out.strip() == expected or EXPECTED_WARNINGS_20230723


class TestMakeJson:
    def test_from_path(self, capsys):
        p1 = "tests/data/sample-2023.07.23/notes"
        testargs = ["makejson", "--path", p1]
        with patch.object(sys, 'argv', testargs):
            totolo.util.validate.main()
        validate1(capsys)

    def test_from_path_narg(self, capsys):
        p1 = "tests/data/sample-2023.07.23/notes"
        testargs = ["makejson", p1]
        with patch.object(sys, 'argv', testargs):
            totolo.util.validate.main()
        validate1(capsys)

    def test_bad_usage(self, capsys):
        testargs = ["makejson", "--path", "foo", "--version", "foo"]
        with patch.object(sys, 'argv', testargs):
            totolo.util.validate.main()
        out, err = capsys.readouterr()
        assert all(x in err for x in ["--path", "--version", "positional"])
        assert not out

    def test_remote_version(self, capsys):
        precache_remote_resources()
        testargs = ["makejson", "--version", "v2023.06"]
        with patch.object(sys, 'argv', testargs):
            with open("tests/data/sample-2023.07.23.tar.gz", "rb+") as fh:
                with patch.object(urllib.request, 'urlopen', return_value=fh):
                    totolo.util.validate.main()
        validate1(capsys)

    def test_remote_version_narg(self, capsys):
        precache_remote_resources()
        testargs = ["makejson", "v2023.06"]
        with patch.object(sys, 'argv', testargs):
            with open("tests/data/sample-2023.07.23.tar.gz", "rb+") as fh:
                with patch.object(urllib.request, 'urlopen', return_value=fh):
                    totolo.util.validate.main()
        validate1(capsys)

    def test_remote_head(self, capsys):
        precache_remote_resources()
        testargs = ["makejson"]
        with patch.object(sys, 'argv', testargs):
            with open("tests/data/sample-2023.07.23.tar.gz", "rb+") as fh:
                with patch.object(urllib.request, 'urlopen', return_value=fh):
                    totolo.util.validate.main()
        validate1(capsys)
