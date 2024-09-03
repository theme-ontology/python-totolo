import shutil


def main():
    """
    Prints helpful info about the ontology and exits.
    """
    print("""
Theme Ontology  https://www.themeontology.org
python-totolo   https://github.com/theme-ontology/python-totolo

To learn more about python usage, follow the github link.

The following commands are provided:
""".strip())
    for command in [
        "mergelist",
        "mergefiles",
        "help",
    ]:
        print(f"  to-{command:<15}" + ("" if shutil.which(command) else "  (not installed)"))
    print("""
Use "command -h" to find out more about each.

Happy Theming!
MO\\PS
""".strip())


if __name__ == "__main__":
    main()
