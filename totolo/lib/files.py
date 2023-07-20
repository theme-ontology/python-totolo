import contextlib
import os
import os.path
import re
import tarfile
import tempfile
import urllib.request
from io import BytesIO


@contextlib.contextmanager
def remote_tar(url: str):
    with tempfile.TemporaryDirectory() as dirname:
        with urllib.request.urlopen(url) as response:
            with tarfile.open(name=None, fileobj=BytesIO(response.read())) as tar:
                tar.extractall(dirname)
        yield dirname


def walk(path: str, pattern: str = ".*", levels: int = -1):
    r = re.compile(pattern)
    # yield matching files
    for item in os.listdir(path):
        spath = os.path.join(path, item)
        if r.match(item):
            if os.path.isfile(spath):
                yield spath
    # recurse
    for item in os.listdir(path):
        spath = os.path.join(path, item)
        if os.path.isdir(spath) and levels != 0:
            for res in walk(spath, pattern, levels - 1):
                yield res
