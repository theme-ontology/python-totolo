import json
import re
import urllib.request

from .impl.parser import TOParser
from .themeontology import ThemeOntology

DEFAULT_URL = "https://github.com/theme-ontology/theming/"
API_URL = "https://api.github.com/repos/theme-ontology/theming/"


def files(paths=None):
    return TOParser.add_files(empty(), paths)


def empty():
    return ThemeOntology()


class TORemote:
    def __call__(self, url: str = "") -> ThemeOntology:
        if not url:
            url = DEFAULT_URL + "archive/refs/heads/master.tar.gz"
        return TOParser.add_url(empty(), url)

    def version(self, version: str = ""):
        if re.match(r"v\d+\.\d+\.\d+$", version):
            url = DEFAULT_URL + f"archive/refs/tags/{version}.tar.gz"
        elif re.match(r"v20\d{2}\.\d{2}$", version):
            url = DEFAULT_URL + f"archive/refs/tags/{version}.tar.gz"
        else:
            raise ValueError(f"Unknown version format {version}.")
        return self(url)

    def versions(self):
        url = API_URL + "releases"
        with urllib.request.urlopen(url) as response:
            contents = response.read()
        for item in json.loads(contents):
            yield item["tag_name"], item["name"]
