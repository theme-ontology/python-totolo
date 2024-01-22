import os
import os.path
import urllib.request
from unittest.mock import patch

from totolo.lib.files import remote_tar, walk


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
