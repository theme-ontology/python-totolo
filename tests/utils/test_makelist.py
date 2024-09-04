import os.path
import sys
import tempfile
from unittest.mock import patch

import pytest

import totolo
import totolo.util.makelist


@pytest.fixture()
def tmpfiles():
    with tempfile.TemporaryDirectory() as basepath:
        p1 = "tests/data/sample-2023.07.23/notes"
        p2 = os.path.join(basepath, "p2.xlsx")
        yield basepath, p1, p2


class TestMakeList:
    def test_basic(self, tmpfiles):
        _basepath, p1, p2 = tmpfiles
        testargs = [
            "makelist", p1, p2, "-d", "-a", "-s", "-t",
            "love",
            "movie: Dr. Jekyll and Mr. Hyde (1920 II)",
        ]
        with patch.object(sys, 'argv', testargs):
            totolo.util.makelist.main()
        assert os.path.isfile(p2)

    def test_regex(self, tmpfiles):
        _basepath, p1, p2 = tmpfiles
        testargs = [
            "makelist", p1, p2, "-t", "-r",
            "^l.ve$",
        ]
        with patch.object(sys, 'argv', testargs):
            totolo.util.makelist.main()
        assert os.path.isfile(p2)

    def test_stories_only(self, tmpfiles):
        _basepath, p1, p2 = tmpfiles
        testargs = [
            "makelist", p1, p2, "-s", "-r",
            ".*Dr. Jekyll",
        ]
        with patch.object(sys, 'argv', testargs):
            totolo.util.makelist.main()
        assert os.path.isfile(p2)
