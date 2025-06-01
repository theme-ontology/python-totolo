import totolo
import os.path


def example_read_write():
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


def example_iterate():
    ontology = totolo.remote()

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


def example_cross_reference():
    ontology = totolo.remote()
    story = ontology.story["play: Macbeth (1606)"]

    #: fetch any stories that have several major/choice themes in common
    weight = ["choice", "major"]
    theme_set = story.themes(weight)
    story_set = {st for st in ontology.stories() if len(st.themes(weight) & theme_set) >= 5}
    print(sorted(st.name for st in story_set))

    # ['movie: Ran (1985)', 'movie: Star Wars: Episode III - Revenge of the Sith (2005)', (...)
    print("---")


if __name__ == "__main__":
    example_read_write()
    example_iterate()
    example_cross_reference()
