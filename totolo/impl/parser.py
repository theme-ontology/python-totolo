import os
import re
import weakref
from itertools import islice
from typing import Generator, Iterable, List, Tuple

import totolo.lib.files
import totolo.lib.textformat

from ..story import TOStory
from ..theme import TOTheme
from .field import TOField
from .keyword import TOKeyword

G = r"[^\<\>\{\}\[\]]"
KW_PATTERN = re.compile("([\\[\\]\\{\\}\\<\\>\\n])")
KW_PATTERN2 = re.compile(f"(^{G}*|\\<{G}*\\>|\\[{G}*\\]|{{{G}*\\}})")


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
    def iter_kwitems(
        lines: Iterable[str]
    ) -> Generator[Tuple[str, str, str, str], None, None]:
        """
        Turn a list of strings into kewyword items.
        Items are un-enclosed newline character separated.
        Items may contain data in () [] {} parentheses.
        Parantheses may not contain newline characters.

        This is one of the most time consuming passages in parsing a large ontology.
        """
        brackets = "<[{"
        for line in lines:
            row = ["", "", "", ""]
            parts = KW_PATTERN2.findall(line)
            for part in parts:
                if part:
                    try:
                        idx = brackets.index(part[0])
                        row[idx + 1] = part[1:-1].strip()
                    except ValueError:
                        row[0] = part.strip()
            if row[0]:
                yield row

    @staticmethod
    def iter_kwitems_strict(
        lines: Iterable[str]
    ) -> Generator[Tuple[str, str, str, str], None, None]:
        """
        Turn a list of strings into kewyword items.
        Items are un-enclosed newline character separated.
        Items may contain data in () [] {} parentheses.
        Parantheses may contain newline characters.

        This is one of the most time consuming passages in parsing a large ontology.
        """
        ramp = " <[{>]}"
        for line in lines:
            field_array = KW_PATTERN.split(line)
            state_idx = 0
            close_bracket = ""
            acc = []
            row = ["", "", "", ""]

            for part in field_array:
                if len(part) == 1 and part in ramp:
                    row[state_idx] += "".join(acc)
                    acc = []
                    if part == close_bracket:
                        state_idx = 0
                        close_bracket = ""
                    elif close_bracket:
                        raise AssertionError(f"Missing '{close_bracket}' in: {row}")
                    else:
                        state_idx = ramp.index(part)
                        if state_idx > 3:
                            raise AssertionError(f"Unexpected {part} in: {row}")
                        close_bracket = ramp[state_idx + 3]
                else:
                    acc.append(part)

            row[state_idx] += "".join(acc)
            if row[0]:
                yield tuple(x.strip() for x in row)

    @classmethod
    def make_field(cls, lines, fieldtype):
        return TOField(
            fieldtype=fieldtype,
            name=lines[0].strip(": "),
            source=list(lines),
        )

    @classmethod
    def init_field(cls, field):
        fieldtype = field.fieldtype
        field.parts.clear()
        if fieldtype == "kwlist":
            data_iter = islice(field.source, 1, 1000)
            for kwtuple in TOParser.iter_kwitems(data_iter):
                field.parts.append(TOKeyword(*kwtuple))
        elif fieldtype == "list":
            data_iter = filter(None, islice(field.source, 1, 1000))
            field.parts.extend(data_iter)
        elif fieldtype == "text":
            field.parts.append("\n".join(field.source[1:]).strip())
        else:  # for datatype "date" and  "blob"
            field.parts.append('\n'.join(field.source[1:]).strip())
        return field

    @classmethod
    def populate_entry(cls, entry, lines):
        entry.source.extend(lines)
        entry.name = lines[0]
        for fieldlines in cls.iter_fields(lines):
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
            if entry.subtype()=="collection":
                collection_entry = entry if idx == 0 else None
            entries.append(entry)
        if collection_entry:
            for entry in entries[1:]:
                field = collection_entry.setdefault("Component Stories")
                field.parts.append(entry.sid)
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
