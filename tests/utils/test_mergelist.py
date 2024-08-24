import os.path
import shutil
import sys
import tempfile
from unittest.mock import patch

import pytest

import totolo
import totolo.util.mergelist


@pytest.fixture()
def tmpfiles():
    with tempfile.TemporaryDirectory() as basepath:
        p1 = "tests/data/sample-2023.07.23/notes/stories/film/film-scifi-1920s.st.txt"
        p2 = "tests/data/scifi1920-mergelist.xlsx"
        p3 = os.path.join(basepath, "p3.st.txt")
        p4 = os.path.join(basepath, "p4.xlsx")
        shutil.copy(p1, p3)
        shutil.copy(p2, p4)
        yield basepath, p1, p2, p3, p4


class TestMergeList:
    def test_dryrun(self, tmpfiles):
        _basepath, p1, _p2, p3, p4 = tmpfiles
        testargs = ["mergefiles", "--dryrun", p4, p3]
        with patch.object(sys, 'argv', testargs):
            totolo.util.mergelist.main()
        assert totolo.files(p1) == totolo.files(p3)

    def test_merge(self, tmpfiles):
        _basepath, p1, _p2, p3, p4 = tmpfiles
        testargs = ["mergefiles", p4, p3]
        with patch.object(sys, 'argv', testargs):
            totolo.util.mergelist.main()
        to = totolo.files(p3)
        s = to["movie: Algol: Tragedy of Power (1920)"]
        assert s.get("Major Themes").parts[0].keyword == "love"
        assert s.get("Major Themes").parts[0].motivation == "foo"

    def test_deletreplace_raises(self, tmpfiles):
        to = totolo.files(tmpfiles[0])
        with pytest.raises(ValueError):
            totolo.util.mergelist.merge_deletions(
                to,
                {('foo', 'bar', 'baz'): True},
                {('foo', 'bar', 'baz'): [('a', 'b', 'c', 'd')]},
            )

    def test_badsheet_raises(self, tmpfiles):
        with pytest.raises(ValueError):
            list(totolo.util.mergelist.read_theme_sheet(tmpfiles[2], sheetpattern="error1"))

    def test_badrow_raises(self):
        rows = [totolo.util.mergelist.LabeledRow(
            headers=["sid", "theme", "weight", "revised motivation"],
            row=["foo", "bar", "baz", "dudd"],
        )]
        rows[0].rtheme = ''
        with pytest.raises(ValueError):
            totolo.util.mergelist.get_changes(rows, totolo.empty())

    def test_labeledrow_str(self):
        lr = totolo.util.mergelist.LabeledRow(
            headers=["sid", "theme", "weight", "revised motivation"],
            row=["foo", "bar", "baz", "dudd"*10],
        )
        slr = str(lr)
        assert 'sid' in slr
        assert 'theme' in slr
        assert 'rmotivation' in slr

    def test_labeledrow_raises(self):
        with pytest.raises(ValueError):
            totolo.util.mergelist.LabeledRow(
                headers=["sid", "theme", "weight", "revised motivation"],
                row=["", "bar", "baz", "dudd"*10],
            )
        with pytest.raises(ValueError):
            totolo.util.mergelist.LabeledRow(
                headers=["sid", "theme", "weight", "revised motivation"],
                row=["foo", "", "", "dudd"*10],
            )
        with pytest.raises(ValueError):
            totolo.util.mergelist.LabeledRow(
                headers=["sid", "theme", "weight", "revised motivation"],
                row=["foo", "bar", "baz", ""],
            )

    def test_get_fieldname(self):
        assert totolo.util.mergelist.get_fieldname("major") == "Major Themes"
        assert totolo.util.mergelist.get_fieldname("Major Themes") == "Major Themes"
        with pytest.raises(ValueError):
            totolo.util.mergelist.get_fieldname("FooBar")
