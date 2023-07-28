import copy
import os.path
import random
from collections import defaultdict

from .impl.core import TOObject, a


class TODict(dict):
    pass


class ThemeOntology(TOObject):
    theme = a(TODict())
    story = a(TODict())
    entries = a({})
    basepaths = a(set())

    def __len__(self):
        return sum(len(v) for v in self.entries.values())

    def __str__(self):
        return f"<{len(self.theme)} themes, {len(self.story)} stories>"

    def stories(self):
        for story in self.story.values():
            yield story

    def themes(self):
        for theme in self.theme.values():
            yield theme

    def astory(self):
        return random.sample(list(self.story.values()), 1)[0]

    def atheme(self):
        return random.sample(list(self.theme.values()), 1)[0]

    def dataframe(self, implied_themes=True):
        import pandas as pd  # pylint: disable=C0415
        data = []
        for story in self.stories():
            for weight, part in story.iter_theme_entries():
                themes = [part.keyword]
                if implied_themes and part.keyword in self.theme:
                    theme = self.theme[part.keyword]
                    themes.extend(theme.ancestors())
                data.append([story.name, story["Title"],
                            story["Date"], part.keyword, weight])
        return pd.DataFrame(
            data, columns=["story_id", "title", "date", "theme", "weight"])

    def validate(self):
        yield from self.validate_entries()
        yield from self.validate_storythemes()
        yield from self.validate_cycles()

    def validate_entries(self):
        """Validate basic format of theme and story entries."""
        lookup = defaultdict(dict)
        for path, entries in self.entries.items():
            for entry in entries:
                for warning in entry.validate():
                    yield f"{path}: {warning}"
                if entry.name in lookup[type(entry)]:
                    tname = type(entry).__name__
                    yield f"{path}: Multiple {tname} with name '{entry.name}'"
                lookup[type(entry)][entry.name] = path

    def validate_storythemes(self):
        """Detect undefined themes used in stories."""
        for story in self.stories():
            for weight in ["choice", "major", "minor", "not"]:
                field = f"{weight.capitalize()} Themes"
                for kwfield in story.get(field):
                    if kwfield.keyword not in self.theme:
                        yield (f"{story.name}: Undefined '{weight} theme' with "
                               f"name '{kwfield.keyword}'")

    def validate_cycles(self):
        """Detect cycles (stops after first cycle encountered)."""
        parents = {}
        for theme in self.themes():
            parents[theme.name] = list(theme.get("Parents"))

        def dfs(current, tpath=None):
            tpath = tpath or []
            if current in tpath:
                cycle = tpath[tpath.index(current):]
                return f"Cycle: {cycle}"
            tpath.append(current)
            for parent in parents[current]:
                msg = dfs(parent, tpath)
                if msg:
                    return msg
            tpath.pop()
            return None

        for theme in self.themes():
            msg = dfs(theme.name)
            if msg:
                yield msg
                break

    def write_clean(self):
        """
        Write the ontology back to its source file while cleaning up syntax and
        omitting unknown field names.
        """
        self.write(cleaned=True)

    def write(self, prefix=None, cleaned=False, verbose=False):
        old_prefix = "" if prefix is None else os.path.commonpath(self.basepaths)
        for path, entries in self.entries.items():
            if prefix is not None:
                rel_path = os.path.relpath(path, old_prefix)
                path = os.path.join(prefix, rel_path)
            self._writefile(path, entries, cleaned)
            if verbose:
                print(f"wrote: {path}")

    def print_warnings(self):
        """
        Run validate and print warnings to stdout.
        """
        for msg in self.validate():
            print(msg)
        return self

    def refresh_relations(self):
        """
        The ontology keeps track of parent/child relations in order to facilitate
        quicker traversal of this hierarchy in both directions, for both themes
        and stories. This method is invoked when the ontology has changed. It is
        invoked automatically by the parser and usually doesn't need to be invoked
        manually.
        """
        for theme in self.themes():
            theme.parents.clear()
            theme.children.clear()
        for story in self.stories():
            story.parents.clear()
            story.children.clear()
        for theme in self.themes():
            for ptheme_name in theme["Parents"]:
                if ptheme_name in self.theme:
                    theme.parents.add(ptheme_name)
                    self.theme[ptheme_name].children.add(theme.name)
        for story in self.stories():
            for pstory_name in story["Collections"]:
                if pstory_name in self.story:
                    story.parents.add(pstory_name)
                    self.story[pstory_name].children.add(story.name)
            for cstory_name in story["Component Stories"]:
                if cstory_name in self.story:
                    story.children.add(cstory_name)
                    self.story[cstory_name].parents.add(story.name)
        return self

    def _writefile(self, path, entries, cleaned):
        cskey = "Component Stories"
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(path, "w", encoding='utf-8') as fhandle:
            sids = set(e.name for e in entries)
            for idx, entry in enumerate(entries):
                if idx == 0 and entry.name in entry["Collections"]:
                    field = entry.get(cskey)
                    parts = [x for x in field.parts if x not in sids]
                    if parts != field.parts:
                        entry = copy.deepcopy(entry)
                        if parts:
                            field = entry.setdefault(cskey)
                            field.parts = parts
                        else:
                            entry.delete(cskey)
                lines = entry.text_canonical() if cleaned else entry.text_original()
                fhandle.write(lines)
                fhandle.write("\n\n" if cleaned else "\n")
