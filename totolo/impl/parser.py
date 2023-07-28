import os
import re
import weakref
from typing import Generator, Iterable, List, Tuple

import totolo.lib.files
import totolo.lib.textformat

from ..story import TOStory
from ..theme import TOTheme
from .field import TOField
from .keyword import TOKeyword


class TOParser:
    @staticmethod
    def iter_entries(lines: Iterable[str]) -> Generator[str, None, None]:
        """
        Iterate through the "entries" in a text file. An entry is a block of lines
        that starts with a title line, followed by a line starting with "===".
        """
        linebuffer = []
        for line in lines:
            line = line.rstrip()
            if line.startswith("===") and linebuffer:
                prevlines = linebuffer[:-1]
                if any(x for x in prevlines):
                    yield prevlines
                linebuffer = [linebuffer[-1]]
            linebuffer.append(line)
        if linebuffer and any(line for line in linebuffer):
            yield linebuffer

    @staticmethod
    def iter_fields(lines: Iterable[str]) -> List[str]:
        """
        Iterate through the fields of an entry. Fields are blocks starting with ::
        """
        linebuffer = []
        for line in lines:
            if line.startswith("::"):
                if linebuffer:
                    yield linebuffer
                linebuffer = [line]
            elif linebuffer:
                linebuffer.append(line)
        if linebuffer:
            yield linebuffer

    @staticmethod
    def iter_listitems(lines: Iterable[str]) -> str:
        """
        Turn a list of strings into items. Items may be newline or comma separated.
        """
        for line in lines:
            # note: once upon a time we used to have multiple items separated by commas
            # on a single line but that is no longer permitted.
            item = line.strip()
            if item:
                yield item

    @staticmethod
    def iter_kwitems(
        lines: Iterable[str]
    ) -> Generator[Tuple[str, str, str, str], None, None]:
        """
        Turn a list of strings into kewyword items. Items may be newline or comma
        separated. Items may contain data in () [] {} parentheses.
        """
        def dict2row(tokendict):
            tkw = tokendict.get("", "").strip()
            tmotivation = tokendict.get("[", "").strip()
            tcapacity = tokendict.get("<", "").strip()
            tnotes = tokendict.get("{", "").strip()
            return tkw, tcapacity, tmotivation, tnotes

        field = "\n".join(lines)
        token = {}
        delcorr = {"[": "]", "{": "}", "<": ">"}
        farr = re.split("([\\[\\]\\{\\}\\<\\>,\\n])", field)
        state = ""
        splitters = ",\n"

        for part in farr:
            if part in delcorr:
                state = part
            elif part in delcorr.values():
                if delcorr.get(state, None) == part:
                    state = ""
                else:
                    raise AssertionError(
                        f"Malformed field (bracket mismatch):\n {field}"
                    )
            elif part in splitters and not state:
                tokrow = dict2row(token)
                if not tokrow[0].strip():
                    pass  # we allow splitting by both newline and comma
                else:
                    yield tokrow
                token = {}
            else:
                token[state] = token.get(state, "") + part

    @classmethod
    def make_field(cls, lines, fieldtype):
        field = TOField(
            fieldtype=fieldtype,
            name=lines[0].strip(": "),
            data=[line.strip() for line in lines[1:] if line.strip()],
            source=list(lines),
        )
        if fieldtype == "kwlist":
            for kwtuple in TOParser.iter_kwitems(field.data):
                field.parts.append(TOKeyword(*kwtuple))
        elif fieldtype == "list":
            for item in TOParser.iter_listitems(field.data):
                field.parts.append(item)
        elif fieldtype == "text":
            field.parts.append(
                totolo.lib.textformat.add_wordwrap(
                    "\n".join(field.data)).strip()
            )
        else:  # date/ blob
            field.parts.append('\n'.join(field.data))
        return field

    @classmethod
    def populate_entry(cls, entry, lines):
        entry.source.extend(lines)
        cleaned = [line.strip() for line in lines]
        assert len(cleaned) > 1 and cleaned[1].startswith("==="), "missing name"
        entry.name = cleaned[0]
        for fieldlines in cls.iter_fields(cleaned):
            name = fieldlines[0].strip(": ")
            fieldtype = entry.field_type(name)
            field = cls.make_field(fieldlines, fieldtype)
            entry[field.name] = field
        return entry

    @classmethod
    def make_story(cls, lines):
        story = cls.populate_entry(TOStory(), lines)
        return story

    @classmethod
    def make_theme(cls, lines):
        theme = cls.populate_entry(TOTheme(), lines)
        return theme

    @classmethod
    def parse_stories(cls, lines):
        collection_entry = None
        entries = []
        for idx, entrylines in enumerate(TOParser.iter_entries(lines)):
            entry = cls.make_story(entrylines)
            if idx == 0:
                mycols = entry.get("Collections").parts
                if mycols and mycols[0] == entry.sid:
                    collection_entry = entry
            if idx > 0 and collection_entry:
                field = collection_entry.setdefault("Component Stories")
                field.parts.append(entry.sid)
            entries.append(entry)
        return entries

    @classmethod
    def parse_themes(cls, lines):
        entries = []
        for _idx, entrylines in enumerate(TOParser.iter_entries(lines)):
            entry = cls.make_theme(entrylines)
            entries.append(entry)
        return entries

    @classmethod
    def add_url(cls, ontology, url):
        suffixes = [".tar", ".tar.gz"]
        if any(url.endswith(x) for x in suffixes):
            with totolo.lib.files.remote_tar(url) as dirname:
                cls.add_files(ontology, dirname)
        else:
            raise ValueError(f"Expected url ending in one of {suffixes}")
        return ontology

    @classmethod
    def add_files(cls, ontology, paths):
        if isinstance(paths, str):
            paths = [paths]
        for path in paths:
            ontology.basepaths.add(path)
            if os.path.isdir(path):
                for filepath in totolo.lib.files.walk(path, r".*\.(st|th)\.txt$"):
                    cls._add_file(ontology, filepath)
            else:
                cls._add_file(ontology, path)
        return ontology.refresh_relations()

    @classmethod
    def _add_file(cls, ontology, path):
        target = {}
        with open(path, "r", encoding='utf-8') as fhandle:
            entry_iterable = []
            if path.endswith(".th.txt"):
                entry_iterable = cls.parse_themes(fhandle)
                target = ontology.theme
            elif path.endswith(".st.txt"):
                entry_iterable = cls.parse_stories(fhandle)
                target = ontology.story
            for entry in entry_iterable:
                entry.source_location = path
                entry.ontology = weakref.ref(ontology)
                ontology.entries.setdefault(path, [])
                ontology.entries[path].append(entry)
                target[entry.name] = entry
        return ontology
