import copy
import os
import os.path
import weakref
from collections import OrderedDict, defaultdict

from ..story import TOStory
from ..theme import TOTheme
from .to_object import TOObject, a
from .to_containers import TODict


class TOBase(TOObject):
    story = a(TODict)
    theme = a(TODict)
    entries = a(dict)
    basepaths = a(set)
    source = a(OrderedDict)

    def __init__(self):
        super().__init__()
        self._impl = TOImpl(self)

    def __len__(self):
        return sum(len(v) for v in self.entries.values())

    def __str__(self):
        return f"ThemeOntology<{len(self.theme)} themes, {len(self.story)} stories>"

    def __iadd__(self, other):
        assert isinstance(other, TOBase)
        other_prefix = os.path.commonpath(other.basepaths)
        self_prefix = os.path.commonpath(self.basepaths)
        for other_path, other_entries in other.entries.items():
            if os.path.commonprefix([other_prefix, other_path]) != other_prefix:
                new_path = other_path  # probably not a path, e.g. '<api>'
            else:
                new_path = os.path.join(self_prefix, os.path.relpath(other_path, other_prefix))
            self_entries = self.entries.setdefault(new_path, [])
            entry_lu = {e.name: e for e in self_entries}
            for other_entry in other_entries:
                if other_entry.name  in entry_lu:
                    entry_lu[other_entry.name] += other_entry
                else:
                    new_entry = copy.deepcopy(other_entry)
                    new_entry.ontology = weakref.ref(self)
                    self_entries.append(new_entry)
                    if isinstance(new_entry, TOStory):
                        self.story[new_entry.name] = new_entry
                    elif isinstance(new_entry, TOTheme):
                        self.theme[new_entry.name] = new_entry
        self.refresh_relations()
        return self

    def __add__(self, other):
        result = copy.deepcopy(self)
        result += other
        return result

    def __eq__(self, other):
        if self.theme != other.theme:
            return False
        if self.story != other.story:
            return False
        return True

    def __contains__(self, obj):
        if isinstance(obj, str):
            return obj in self.story or obj in self.theme
        if isinstance(obj, TOTheme):
            return self.theme.get(obj.name, None) == obj
        if isinstance(obj, TOStory):
            return self.story.get(obj.name, None) == obj
        return False

    def __getitem__(self, key):
        if key in self.theme:
            if key in self.story:
                raise KeyError(f"Ambiguous Key: '{key}' is both a theme and a story.")
            return self.theme[key]
        return self.story[key]

    def __setitem__(self, key, value):
        if not isinstance(value, (TOStory, TOTheme)):
            raise ValueError(
                f"Can only insert TOTheme or TOStory into ontology, not {type(value)}."
            )
        if not value.name:
            value.name = key
        assert value.name == key
        try:
            del self[key]
        except KeyError:
            pass
        if isinstance(value, TOStory):
            self.story[key] = value
        elif isinstance(value, TOTheme):
            self.theme[key] = value
        self.entries.setdefault(value.source_location, []).append(value)
        value.ontology = weakref.ref(self)

    def __delitem__(self, key):
        item = self[key]
        self.entries[item.source_location].remove(item)
        if key in self.theme:
            del self.theme[key]
        if key in self.story:
            del self.story[key]

    def refresh_relations(self):
        """
        The ontology keeps track of parent/child relations in order to facilitate
        quicker traversal of this hierarchy in both directions, for both themes
        and stories. This method is invoked when the ontology has changed. It is
        invoked automatically by the parser and usually doesn't need to be invoked
        manually. It would need to invoke if the structure of the ontology is edited
        outside of the parser.
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

    def organize_collections(self):
        """
        Pull out any collection specified on a story and instead put the story
        as a component on that collection.
        """
        field_list = []
        for story in self.stories():
            for pstory_name in story["Collections"]:
                if  pstory_name != story.name and pstory_name in self.story:
                    comp_field = self.story[pstory_name].setdefault("Component Stories")
                    comp_field.parts.append(story.name)
                    field_list.append(comp_field)
            if not story["Collections"].frozen:
                story["Collections"].parts.clear()
        for fl in field_list:
            fl.parts = sorted(set(fl.parts))
        return self

    def validate(self):
        yield from self._impl.validate_entries()
        yield from self._impl.validate_storythemes()
        yield from self._impl.validate_cycles()

    def write(self, prefix=None, cleaned=False, verbose=False):
        old_prefix = "" if prefix is None else os.path.commonpath(self.basepaths)
        for path, entries in self.entries.items():
            if prefix is not None:
                rel_path = os.path.relpath(path, old_prefix)
                path = os.path.join(prefix, rel_path)
            self._impl.writefile(path, entries, cleaned)
            if verbose:
                print(f"wrote: {path}")


class TOImpl:
    def __init__(self, ontology):
        self.o = ontology

    @staticmethod
    def subset_as_names(subset):
        if hasattr(subset, "names"):
            yield from subset.names()
        elif hasattr(subset, "name"):
            yield subset.name
        elif isinstance(subset, str):
            yield subset
        else:
            for x in subset:
                yield from TOImpl.subset_as_names(x)

    @staticmethod
    def writefile(path, entries, cleaned):
        cskey = "Component Stories"
        collection_entry = None
        dirname = os.path.dirname(path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)
        for idx, entry in enumerate(entries):
            if entry.subtype()=="collection":
                collection_entry = entry if idx == 0 else None
        with open(path, "w", encoding='utf-8') as fhandle:
            sids = set(e.name for e in entries)
            for idx, entry in enumerate(entries):
                if entry is collection_entry:
                    field = entry.get(cskey)
                    all_parts = list(field)
                    parts_ex_implied = [x for x in all_parts if x not in sids]
                    entry = copy.deepcopy(entry)
                    if parts_ex_implied:
                        field = entry.setdefault(cskey)
                        field.parts = parts_ex_implied
                    else:
                        entry.delete(cskey)
                lines = entry.text_canonical() if cleaned else entry.text_original()
                fhandle.write(lines)
                fhandle.write("\n\n" if cleaned else "\n")

    def dataframe_records(
        self,
        subset_stories,
        subset_themes,
        implied_themes,
        motivation,
        descriptions,
    ):
        story_ids = list(self.subset_as_names(subset_stories))
        theme_ids = list(self.subset_as_names(subset_themes))
        headers = ["story_id", "title", "date", "theme_id", "weight"]
        if motivation:
            headers.append("motivation")
        if descriptions:
            headers.append("story_description")
            headers.append("theme_definition")
        data = []
        for story in self.o.stories():
            if story_ids and story.name not in story_ids:
                continue
            records = self.dataframe_records_for_story(
                story,
                implied_themes=implied_themes,
                motivation=motivation,
                descriptions=descriptions,
            )
            if theme_ids:
                records = [r for r in records if r[3] in theme_ids]
            data.extend(records)
        return headers, data

    def dataframe_records_for_story(
        self, story,
        implied_themes=False,
        motivation=False,
        descriptions=False,
    ):
        data = []
        for weight, part in story.iter_theme_entries():
            themes = [part.keyword]
            if implied_themes and part.keyword in self.o.theme:
                theme = self.o.theme[part.keyword]
                themes.extend(t.name for t in theme.ancestors())
            for themename in themes:
                record = [
                    story.name,
                    story["Title"],
                    story["Date"],
                    themename,
                    weight,
                ]
                if motivation:
                    record.append(part.motivation)
                if descriptions:
                    record.append(story.verbose_description())
                    record.append(
                        self.o.theme[themename].verbose_description()
                        if themename in self.o.theme else ""
                    )
                data.append(record)
        return data

    def validate_entries(self):
        """Validate basic format of theme and story entries."""
        lookup = defaultdict(dict)
        for path, entries in self.o.entries.items():
            for entry in entries:
                for warning in entry.validate():
                    yield f"{path}: {warning}"
                if entry.name in lookup[type(entry)]:
                    tname = type(entry).__name__
                    yield f"{path}: Multiple {tname} with name '{entry.name}'"
                lookup[type(entry)][entry.name] = path

    def validate_storythemes(self):
        """Detect undefined themes used in stories."""
        for story in self.o.stories():
            for weight in ["choice", "major", "minor", "not"]:
                field = f"{weight.capitalize()} Themes"
                for kwfield in story.get(field):
                    if kwfield.keyword not in self.o.theme:
                        yield (f"{story.name}: Undefined '{weight} theme' with "
                               f"name '{kwfield.keyword}'")

    def validate_cycles(self):
        """Detect cycles (stops after first cycle encountered)."""
        parents = {}
        for theme in self.o.themes():
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

        for theme in self.o.themes():
            msg = dfs(theme.name)
            if msg:
                yield msg
                break

    def to_dict(self, ont):
        lto = OrderedDict()
        ordered_keys = ["origin", "version", "timestamp", "git-commit-id"]
        for key in ordered_keys:
            lto[key] = ont.source.get(key, "")
        for key, value in sorted(ont.source.items()):
            if key not in ordered_keys:
                lto[key] = value
        return OrderedDict(
            lto = lto,
            themes = [
                th.to_dict()
                for _name, th in sorted(ont.theme.items())
            ],
            stories = [
                st.to_dict()
                for _name, st in sorted(ont.story.items())
                if not st.subtype() == "collection"
            ],
            collections = [
                st.to_dict()
                for _name, st in sorted(ont.story.items())
                if st.subtype() == "collection"
            ],
        )
