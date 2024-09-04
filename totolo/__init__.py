"""
The Python interface to themeontology.org.
"""

__version__ = "1.7.1"

from totolo.api import TORemote, empty, files

remote = TORemote()

__ALL__ = [
    empty,
    files,
    remote,
]
