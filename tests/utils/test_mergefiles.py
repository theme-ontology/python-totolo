import os.path
import shutil
import sys
import tempfile
from unittest.mock import patch

import pytest

import totolo
import totolo.util.mergefiles


@pytest.fixture()
def tmpfiles():
    with tempfile.TemporaryDirectory() as basepath:
        p1 = "tests/data/sample-2023.07.23/notes/stories/film/film-scifi-1920s.st.txt"
        p2 = "tests/data/sample-2023.07.23/notes/stories/film/film-scifi-1930s.st.txt"
        p3 = os.path.join(basepath, "p3.st.txt")
        p4 = os.path.join(basepath, "p4.st.txt")
        shutil.copy(p1, p3)
        shutil.copy(p2, p4)
        yield basepath, p1, p2, p3, p4


class TestMergeFiles:
    def test_nonsense(self, tmpfiles):
        _basepath, _p1, p2, _p3, p4 = tmpfiles
        testargs = ["mergefiles", "--dryrun", "--reorder", "/dev/null/foobar", p4]
        with patch.object(sys, 'argv', testargs):
            totolo.util.mergefiles.main()
        assert totolo.files(p2) == totolo.files(p4)

    def test_dryrun(self, tmpfiles):
        _basepath, _p1, p2, p3, p4 = tmpfiles
        testargs = ["mergefiles", "--dryrun", "--reorder", p3, p4]
        with patch.object(sys, 'argv', testargs):
            totolo.util.mergefiles.main()
        assert totolo.files(p2) == totolo.files(p4)

    def test_mixing(self, tmpfiles):
        basepath, _p1, p2, p3, p4 = tmpfiles
        testargs = ["mergefiles", "--dryrun", "--reorder", basepath, p3, p4]
        with patch.object(sys, 'argv', testargs):
            totolo.util.mergefiles.main()
        assert totolo.files(p2) == totolo.files(p4)

    def test_files(self, tmpfiles):
        _basepath, p1, p2, p3, p4 = tmpfiles
        testargs = ["mergefiles", p3, p4]
        with patch.object(sys, 'argv', testargs):
            totolo.util.mergefiles.main()
        t1 = totolo.files(p4)
        for story in totolo.files([p1, p2]).stories():
            assert story.name in t1
            if not story.name.startswith("Collection:"):
                assert story in t1
