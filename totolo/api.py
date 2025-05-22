import json
import urllib.request
import functools

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
        version = "none"
        sha = "none"
        timestamp = "none"
        if not url:
            url = DEFAULT_URL + "archive/refs/heads/master.tar.gz"
            version = "latest/master"
            sha = self._get("commits/master")["sha"]
            timestamp = self._get("commits/master")["commit"]["committer"]["date"]
        ontology = TOParser.add_url(empty(), url)
        ontology.source.update({
            "origin": url,
            "version": version,
            "timestamp": timestamp,
            "git-commit-id": sha,
        })
        return ontology

    def version(self, version: str = ""):
        sha = "none"
        for release in self._get("releases"):
            if version == release["tag_name"]:
                url = DEFAULT_URL + f"archive/refs/tags/{version}.tar.gz"
                timestamp = release["published_at"]
                break
        else:
            raise ValueError(f"Unknown version {version}. Check list(totolo.remote.versions()).")
        for tag in self._get("tags"):
            if tag["name"] == version:
                sha = tag["commit"]["sha"]
                break
        if sha:
            timestamp = self._get("commits/" + sha)["commit"]["committer"]["date"]
        ontology = self(url)
        ontology.source.update({
            "version": version,
            "timestamp": timestamp,
            "git-commit-id": sha,
        })
        return ontology

    def versions(self):
        for item in self._get("releases"):
            yield item["tag_name"], item["name"]

    @functools.lru_cache
    def _get(self, endpoint):
        url = API_URL + endpoint
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read())
