import totolo
import os.path


def example():
    #: get the latest main branch version of the ontology
    ontology = totolo.remote()
    print(ontology)

    # <2945 themes, 4475 stories>
    #: use ontology.print_warnings() to check if there are any formatting issues
    print("---")

    home = os.path.expanduser('~')
    ontology.write(f"{home}/themes")
    ontology_local = totolo.files(f"{home}/themes")
    print(ontology_local)

    # <2945 themes, 4475 stories>
    print("---")

    #: go over all the themes
    for theme in ontology.themes():
        if "romantic love" in theme.name:
            print(theme)

    # b'personal freedom vs. romantic love'[3]
    # b'romantic love'[3]
    print("---")

    #: check the definition of a theme
    love = ontology.theme["love"]
    love.print()

    # (...)
    print("---")

    #: fetch a story and go over the themes therein
    story = ontology.story["play: Macbeth (1606)"]
    for weight, theme in story.iter_themes():
        print(f"{weight:<10} {theme.name}")

    # (...)
    print("---")


if __name__ == "__main__":
    example()
