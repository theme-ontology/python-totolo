import argparse
import json
import re
import sys
from collections import defaultdict

import totolo


THEME_FIELDS_OFFICIAL = {
    "name": "always",
    "aliases": "ifset",
    "description": "always",
    "examples": "ifset",
    "notes": "ifset",
    "parents": "always",
    "references": "always",
}


STORY_FIELDS_OFFICIAL = {
    "name": "always",
    "authors": "ifset",
    "collections": "ifset",
    "component stories": "ifset",
    "date": "always",
    "description": "always",
    "references": "always",
    "related stories": "ifset",
    "title": "always",
    "variation": "ifset",
    "themes": "always",
}


def filter_dict(dd, lookup):
    for key in list(dd):
        try:
            spec = lookup[key]
        except KeyError:
            spec = None
        if not spec or (spec == "ifset" and not dd[key]):
            del dd[key]
    return dd


def include_theme(th_dict):
    return bool(th_dict)


def convert_theme(th_dict, verbosity="official"):
    return filter_dict(
        th_dict,
        THEME_FIELDS_OFFICIAL if verbosity=="official" else defaultdict(lambda: "always")
    )


def include_story(st_dict):
    for key, val in st_dict.items():
        if key.endswith(" themes"):
            if val:
                return True
    return False


def convert_story(st_dict, verbosity="official"):
    combined_themes = []
    for key in list(st_dict):
        if key.endswith(" themes"):
            kwlist = st_dict.pop(key)
            assert isinstance(kwlist, list)
            for kw_as_dict in kwlist:
                kw_as_dict["level"] = key.split(" ", 1)[0].lower()
            combined_themes.extend(kwlist)
    st_dict["themes"] = combined_themes
    return filter_dict(
        st_dict,
        STORY_FIELDS_OFFICIAL if verbosity=="official" else defaultdict(lambda: "always")
    )


def make_json(ontology,
    with_themes=True,
    with_stories=True,
    with_collections=True,
    verbosity="official",
):
    dd = ontology.to_dict()
    lto = dd["lto"]
    themes = [convert_theme(td, verbosity) for td in dd.pop("themes") if include_theme(td)]
    stories = [convert_story(sd, verbosity) for sd in dd.pop("stories") if include_story(sd)]
    collections = [convert_story(sd, verbosity) for sd in dd.pop("collections")]
    lto["encoding"] = "UTF-8"
    lto["theme-count"] = len(themes)
    lto["story-count"] = len(stories)
    lto["collection-count"] = len(collections)
    if with_themes:
        dd["themes"] = themes
    if with_stories:
        dd["stories"] = stories
    if with_collections:
        dd["collections"] = collections
    return dd


def main():
    """
    This utility is provided as a command line script.

    Example:
        "to-makejson v2025.04 -tsc > ontology_v202404.json"
    """
    version_patt = re.compile("v\\d{4}\\.\\d{2}$")
    parser = argparse.ArgumentParser(
        description=(
            "Output a version of the ontology as json. "
            "Use -t -s -c to select themes, stories, and/or collections respectively. "
            "If none of these flags are given, all will be included. "
        ),
        epilog=main.__doc__
    )
    parser.add_argument("source", nargs="*", help=
        "Paths to include or version to download. "
        "If a single argument matching tag pattern vYYYY.MM is given, "
        "it will be interpreted as a version. "
        "Otherwise the arguments will be treated as one or more local paths. "
    )
    parser.add_argument("-p", "--path", help="Path to the ontology.")
    parser.add_argument("--verbosity", default="official", help=
        "Which fields to include. "
        "'official': (default) include fields for official release. "
        "'all': include all fields. "
    )
    parser.add_argument(
        "-v", "--version", help="Named version to use. If not specified the latest version of the "
        "master branch will be used."
    )
    parser.add_argument("-t", action='store_true', help="Include themes.")
    parser.add_argument("-s", action='store_true', help="Include stories.")
    parser.add_argument("-c", action='store_true', help="Include collections.")
    parser.add_argument('--reorg', action=argparse.BooleanOptionalAction, default=True, help=
        "If set (default) reorganize the ontology in some ways. "
        "In particular, remove collection entries on stories and add corresponding "
        "component entries on the collections instead. "
    )
    args = parser.parse_args()

    if sum(1 for x in [args.path, args.version, args.source] if x) > 1:
        sys.stderr.write("Can specify at most one of --path, --version, or positional argument.")
        return
    if args.source:
        if len(args.source) == 1 and version_patt.match(args.source[0]):
            ontology = totolo.remote.version(args.source[0])
        else:
            ontology = totolo.files(args.source)
    elif args.path:
        ontology = totolo.files(args.path)
    elif args.version:
        ontology = totolo.remote.version(args.version)
    else:
        ontology = totolo.remote()

    if args.reorg:
        ontology.organize_collections()

    if not any([args.t, args.s, args.c]):
        dd = make_json(ontology, verbosity=args.verbosity)
    else:
        dd = make_json(
            ontology,
            with_themes=args.t,
            with_stories=args.s,
            with_collections=args.c,
            verbosity=args.verbosity,
        )

    try:
        print(json.dumps(dd, indent=4, ensure_ascii=False))
    except BrokenPipeError:  # pragma: no cover
        pass


if __name__ == "__main__":
    main()
