"""
The Python interface to themeontology.org.
"""
from totolo.impl.api import TORemote, empty, files


remote = TORemote()
__version__ = "2.1.2"
__ALL__ = [
    empty,
    files,
    remote,
]
