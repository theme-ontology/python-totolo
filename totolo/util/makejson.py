import argparse
import json

import totolo


def include_theme(th_dict):
    return bool(th_dict)


def convert_theme(th_dict):
    return th_dict


def include_story(st_dict):
    for key, val in st_dict.items():
        if key.endswith(" themes"):
            if val:
                return True
    return False


def convert_story(st_dict):
    combined_themes = []
    for key in list(st_dict):
        if key.endswith(" themes"):
            kwlist = st_dict.pop(key)
            assert isinstance(kwlist, list)
            for kw_as_dict in kwlist:
                kw_as_dict["level"] = key.split(" ", 1)[0].lower()
            combined_themes.extend(kwlist)
    st_dict["themes"] = combined_themes
    return st_dict


def make_json(ontology, with_themes=True, with_stories=True, with_collections=True):
    dd = ontology.to_dict()
    lto = dd["lto"]
    themes = [convert_theme(td) for td in dd.pop("themes") if include_theme(td)]
    stories = [convert_story(sd) for sd in dd.pop("stories") if include_story(sd)]
    collections = [convert_story(sd) for sd in dd.pop("collections")]
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
    print(json.dumps(dd, indent=4, ensure_ascii=False))


def main():
    """
    This utility is provided as a command line script.

    Example:
        "to-makejson "
    """
    parser = argparse.ArgumentParser(
        description=(
            'Output a version of the ontology as json.'
            'Use -t -s -c to select themes, stories, and/or collections.'
            'If none of these flags are given, all will be included.'
        ),
        epilog=main.__doc__
    )
    parser.add_argument("-p", "--path", help="Path to the ontology.")
    parser.add_argument(
        "-v", "--version", help="Named version to use. If not specified the latest version of the "
        "master branch will be used."
    )
    parser.add_argument("-t", action='store_true', help="Include themes.")
    parser.add_argument("-s", action='store_true', help="Include stories.")
    parser.add_argument("-c", action='store_true', help="Include collections.")
    args = parser.parse_args()

    if args.path and args.version:
        print("Can't specify both --path and --version.")
        return
    if args.path:
        ontology = totolo.files(args.path)
    elif args.version:
        ontology = totolo.remote.version(args.version)
    else:
        ontology = totolo.remote()

    try:
        if not any([args.t, args.s, args.c]):
            make_json(ontology)
        else:
            make_json(ontology, with_themes=args.t, with_stories=args.s, with_collections=args.c)
    except BrokenPipeError:  # pragma: no cover
        pass


if __name__ == "__main__":
    main()
