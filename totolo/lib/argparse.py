import argparse
import re
import sys

import totolo


VERSION_PATTERN = re.compile("v\\d{4}\\.\\d{2}$")


def get_parser(description, epilog):
    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
    )
    parser.add_argument("source", nargs="*", help=
        "Paths to include or version to download. "
        "If a single argument matching tag pattern vYYYY.MM is given, "
        "it will be interpreted as a version. "
        "Otherwise the arguments will be treated as one or more local paths. "
    )
    parser.add_argument("-p", "--path", help="Path to the ontology.")
    parser.add_argument(
        "-v", "--version", help="Named version to use. If not specified the latest version of the "
        "master branch will be used."
    )
    return parser


def get_ontology(args, quiet=True):
    if sum(1 for x in [args.path, args.version, args.source] if x) > 1:
        print("Can specify at most one of --path, --version, or positional argument.",
              file=sys.stderr)
        return None
    if args.source:
        if len(args.source) == 1 and VERSION_PATTERN.match(args.source[0]):
            if not quiet:
                print(f":: loading TO version {args.source[0]}", file=sys.stderr)
            ontology = totolo.remote.version(args.source[0])
        else:
            if not quiet:
                print(f":: loading TO files {args.source}", file=sys.stderr)
            ontology = totolo.files(args.source)
    elif args.path:
        if not quiet:
            print(f":: loading TO files {args.path}", file=sys.stderr)
        ontology = totolo.files(args.path)
    elif args.version:
        if not quiet:
            print(f":: loading TO version {args.version}", file=sys.stderr)
        ontology = totolo.remote.version(args.version)
    else:
        if not quiet:
            print(":: loading TO working HEAD version", file=sys.stderr)
        ontology = totolo.remote()
    return ontology
