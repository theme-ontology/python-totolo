import os.path
import argparse

import totolo

from ..lib import log


def mergefiles(paths, reorder=True, dryrun=False):
    final_to = None
    isdir = []

    for _idx, path in enumerate(reversed(paths)):
        if not os.path.exists(path):
            log.warning(f"Doesn't exist: {path}")
            continue
        isdir.append(os.path.isdir(path))
        to = totolo.files(path)
        log.info(f"Read {'dir' if isdir[-1] else 'file'}: {path}")
        if final_to:
            final_to += to
        else:
            final_to = to

    if len(isdir) != len(paths):
        return
    if not any(isdir):
        destination_path = paths[-1]
        all_entries = sum(final_to.entries.values(), [])
        for entry in all_entries:
            entry.source_location = destination_path
        final_to.entries = {destination_path: all_entries}
    elif not all(isdir):
        log.warning("Can't mix directories and files in arguments - aborting.")
        return

    for path, entries in final_to.entries.items():
        if reorder:
            entries.sort(key=lambda x: (
                1 if x.subtype()=="collection" else 2,
                x.name.casefold(),
                x.name
            ))
        prefix = "Would have written" if dryrun else "Writing"
        log.info(f"{prefix}: {path}: {len(entries)} entries")

    if not dryrun:
        final_to.write_clean()


def main():
    """
    This utility is provided as a command line script.

    Example:
        "to-mergefiles file1 file2 fileN".
    """
    parser = argparse.ArgumentParser(
        description=(
            'Merge a number of files, or a number of dirs.'
        ),
        epilog=main.__doc__
    )
    parser.add_argument(
        "paths",
        help="One or more paths. The paths must all point to files, or all point to dirs.",
        nargs='*'
    )
    parser.add_argument(
        "--dryrun",
        help="Read and report on stdout, but do not write changes to final path.",
        action="store_true",
    )
    parser.add_argument(
        "--reorder",
        help="If set, reorder the entries in each file alphabetically.",
        action="store_true",
    )
    args = parser.parse_args()
    mergefiles(args.paths, reorder=args.reorder, dryrun=args.dryrun)


if __name__ == "__main__":
    main()
