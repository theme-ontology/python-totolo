import totolo


def example():
    #: get the latest main branch version of the ontology
    ontology = totolo.remote()
    print(ontology)
    # <2945 themes, 4475 stories>
    # ontology.print_warnings()
    print("---")
    ontology.write("/home/mo/themes")
    ontology = totolo.files("/home/mo/themes")
    print(ontology)
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
    print("---")


if __name__ == "__main__":
    example()
