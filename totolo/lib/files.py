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
        paths = [os.path.join(dirname, x) for x in os.listdir(dirname)]
        # we expect a single (irrelevant) dir here as git wraps everything thus
        if len(paths) == 1 and os.path.isdir(paths[0]):
            yield paths[0]
        else:
            yield dirname


def walk(path: str, pattern: str = ".*", levels: int = -1):
    regex = re.compile(pattern)

    for item in os.listdir(path):
        spath = os.path.join(path, item)
        if regex.match(item):
            if os.path.isfile(spath):
                yield spath

    for item in os.listdir(path):
        spath = os.path.join(path, item)
        if os.path.isdir(spath) and levels != 0:
            yield from walk(spath, pattern, levels - 1)
