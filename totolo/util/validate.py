import totolo.lib.argparse


def main():
    """
    This utility is provided as a command line script.

    Example:
        "to-validate v2025.04"
    """
    parser = totolo.lib.argparse.get_parser(
        "Load a version of the ontology and print any warnings about syntax. ",
        main.__doc__
    )
    ontology = totolo.lib.argparse.get_ontology(parser.parse_args(), quiet=False)
    try:
        if ontology:
            ontology.print_warnings()
    except BrokenPipeError:  # pragma: no cover
        pass


if __name__ == "__main__":
    main()
