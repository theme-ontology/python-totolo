import argparse
from collections import defaultdict
from pprint import pprint

import totolo
from totolo.lib import excel, log


REQUIRED_HEADERS = [
    "sid", "weight", "theme", "motivation", "revised theme", "revised weight",
    "revised motivation"
]

OPTIONAL_HEADERS = ["revised capacity", "action"]

FIELDNAMES = {
    "minor": "Minor Themes",
    "major": "Major Themes",
    "choice": "Choice Themes",
}


def get_fieldname(field_alias_or_name):
    if field_alias_or_name in FIELDNAMES:
        return FIELDNAMES[field_alias_or_name]
    if field_alias_or_name in FIELDNAMES.values():
        return field_alias_or_name
    raise ValueError(f"Unknown field name referenced: {field_alias_or_name}")


class LabeledRow:
    def __init__(self, headers, row):
        for hh, rr in zip(headers, row):
            attr = self._hhattr(hh)
            setattr(self, attr, rr.strip())
        for hh in REQUIRED_HEADERS + OPTIONAL_HEADERS:
            attr = self._hhattr(hh)
            if not hasattr(self, attr):
                setattr(self, attr, "")

        if not self.sid:
            raise ValueError(f"Entry without Story ID: {self}.")
        if self.action.lower() == "delete":
            self.rmotivation = ''
            self.rtheme = ''
            self.rweight = ''
            self.rcapacity = ''
        else:
            self.rtheme = self.rtheme or self.theme
            self.rweight = self.rweight or self.weight
            self.rmotivation = self.rmotivation or self.motivation
            if not (self.rtheme and self.rweight):
                raise ValueError(f"Revised entry without identifying theme/weight: {self}.")
            if not self.rmotivation:
                raise ValueError(f"Revised entry without motivation: {self}.")

    def __str__(self):
        parts = []
        for hh in REQUIRED_HEADERS:
            attr = self._hhattr(hh)
            if hasattr(self, attr):
                value = getattr(self, attr)
                if value:
                    if len(value) > 10:
                        value = value[:8] + '..'
                    parts.append(f'{attr}:{value}')
        return '{' + ', '.join(parts) + '}'

    def _hhattr(self, hh):
        hhparts = hh.split()
        return ''.join(x[0] for x in hhparts[:-1]) + hhparts[-1]


def read_theme_sheet(filename, sheetpattern="data"):
    headers = excel.get_headers(filename, sheetpattern=sheetpattern)[0][1]
    for hh in REQUIRED_HEADERS:
        if hh not in headers:
            raise ValueError(f"Missing header: {hh}")
    activeheaders = list(REQUIRED_HEADERS)
    for hh in OPTIONAL_HEADERS:
        if hh in headers:
            activeheaders.append(hh)
    log.info("Reading named columns from %s: %s", filename, activeheaders)
    data, sheetcount, rowcount = excel.read_xls(
        filename, headers=activeheaders, sheetpattern=sheetpattern
    )
    log.info("Read %s rows from %s sheets.", rowcount, sheetcount)
    for row in data:
        yield LabeledRow(activeheaders, row)


def get_rows(listpath):
    yield from read_theme_sheet(listpath)


def get_changes(rows, ontology):
    newentries = defaultdict(lambda: defaultdict(list))
    replacements = defaultdict(list)
    deletions = defaultdict(bool)
    new_themes = defaultdict(list)

    for row in rows:
        if not row.theme or not row.weight:
            newentries[row.sid][row.rweight].append([
                row.rtheme, row.rmotivation, row.rcapacity
            ])
        elif row.rtheme and row.rweight:
            if row.weight == row.rweight:
                replacements[(
                    row.sid, row.weight, row.theme)].append(
                    (row.rweight, row.rtheme, row.rmotivation, row.rcapacity)
                )
            else:
                deletions[(row.sid, row.weight, row.theme)] = True
                newentries[row.sid][row.rweight].append([
                    row.rtheme, row.rmotivation, row.rcapacity
                ])
        elif not any([row.rtheme, row.rweight, row.rmotivation, row.rcapacity]):
            deletions[(row.sid, row.weight, row.theme)] = True
        else:
            raise ValueError(f"Unexpected row configuration: {row}")
        if row.rtheme and row.rtheme not in ontology.theme:
            new_themes[row.rtheme] = row.theme

    return newentries, replacements, deletions, new_themes


def report_changes(newentries, replacements, deletions, new_themes):
    print()
    print("NEW")
    for sid in newentries:
        print(sid)
        pprint(dict(newentries[sid]))
    print("REPLACEMENT")
    pprint(dict(replacements))
    print("DELETION")
    pprint(dict(deletions))

    for newtheme, previous in new_themes.items():
        log.warning("Undefined New Theme: %s CHANGED FROM %s", newtheme, sorted(set(previous)))


def merge_deletions(ontology, deletions, replacements):
    for key in deletions:
        (sid, oldweight, oldtheme) = key
        if key in replacements:
            raise ValueError(f"Marked for both DELETION and REPLACEMENT: {key}")
        kwfield = ontology.story[sid].get(get_fieldname(oldweight))
        if kwfield.frozen:
            log.error("DELETE TARGET WEIGHT %s MISSING: %s", oldweight, key)
            continue
        count = kwfield.delete_kw(oldtheme)
        assert count <= 1
        if count == 0:
            log.warning("DELETE TARGET ALREADY MISSING: %s", key)


def merge_replacements(ontology, replacements):
    for key in replacements:
        (sid, oldweight, oldtheme) = key
        kwfield = ontology.story[sid].get(get_fieldname(oldweight))
        for nw, nt, nc, ncapacity in replacements[key]:
            assert oldweight == nw, "replacement listed but weights don't match, illogical"
            kwfield.update_kw(
                oldtheme,
                keyword=nt,
                motivation=nc,
                capacity=ncapacity,
            )


def merge_newentries(ontology, newentries):
    for sid in newentries:
        for fieldname in newentries[sid]:
            for theme, motivation, ncapacity in newentries[sid][fieldname]:
                kwfield = ontology.story[sid].setdefault(get_fieldname(fieldname))
                kwfield.insert_kw(
                    keyword=theme,
                    motivation=motivation,
                    capacity=ncapacity,
                )


def mergelist(listpath, notespath, dryrun=False):
    ontology = totolo.files(notespath) if notespath else totolo.empty()
    newentries, replacements, deletions, new_themes = get_changes(get_rows(listpath), ontology)
    if dryrun:
        report_changes(newentries, replacements, deletions, new_themes)
    else:
        merge_deletions(ontology, deletions, replacements)
        merge_replacements(ontology, replacements)
        merge_newentries(ontology, newentries)
        ontology.write_clean()


def main():
    """
    This utility is provided as a command line script.

    Example:
        "to-mergelist mydata.xlsx ./ontology/notes".
    """
    headers = REQUIRED_HEADERS + OPTIONAL_HEADERS
    parser = argparse.ArgumentParser(
        description=(
            'Merge an excel sheet of changes into a theme ontology directory. ' +
            'The first row should contain column headers, including: ' +
            ', '.join(headers) + '.'
        ),
        epilog=main.__doc__
    )
    parser.add_argument("path_changes", help="Path to the Excel sheet with changes.")
    parser.add_argument("path_ontology", help="Path to the ontology.")
    parser.add_argument(
        "--dryrun",
        help="Read and report on stdout, but do not write changes to ontology.",
        action="store_true",
    )
    args = parser.parse_args()
    mergelist(args.path_changes, args.path_ontology, args.dryrun)


if __name__ == "__main__":
    main()
