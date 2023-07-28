import os
import os.path
import urllib.request
from unittest.mock import patch

from totolo.lib.files import remote_tar, walk
from totolo.lib.textformat import add_wordwrap, remove_wordwrap


def test_remove_wordwrap():
    text = """
Lorem ipsum dolor sit
amet, consectetur adipiscing elit, sed
do eiusmod tempor incididunt ut
labore et dolore magna aliqua.

Ut enim ad minim veniam, quis nostrud

exercitation ullamco laboris nisi ut
aliquip ex ea commodo consequat.


Duis aute irure dolor in reprehenderit in
voluptate velit esse cillum dolore eu fugiat
nulla pariatur. Excepteur sint occaecat cupidatat
non proident, sunt in culpa qui officia
deserunt mollit anim id est laborum.
    """.strip()
    text_out = remove_wordwrap(text)
    print(text_out)
    words = text.split()
    words_out = text_out.split()
    assert words == words_out


def test_add_wordwrap():
    text = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod "
        "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, "
        "quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo "
        "consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse "
        "cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non "
        "proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    )
    text_out = add_wordwrap(text)
    print(text_out)
    words = text.split()
    words_out = text_out.split()
    assert words == words_out


def test_remote_tar():
    with open("tests/data/flat.tar.gz", "rb+") as fh:
        with patch.object(urllib.request, 'urlopen', return_value=fh):
            with remote_tar("https://placeholder.tar.gz") as path:
                print(path)
                assert sorted(os.listdir(path)) == [
                    "collections", "stories", "themes"
                ]


def test_walk():
    files = [os.path.split(x)[-1] for x in list(walk("tests/data/sample-2023.07.23"))]
    assert sorted(files) == [
        'film-scifi-1920s.st.txt',
        'film-scifi-1930s.st.txt',
        'primary.th.txt',
        'scifi-collections.st.txt',
        'timeperiod.th.txt',
    ]
