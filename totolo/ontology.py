import random

from .impl.to_base import TOBase


class ThemeOntology(TOBase):
    """
    Common API for the Theme Ontology.
    These methods have the highest degree of support. See TOBase for more methods.
    Use brackets like `ontology[name]` to access uniquely named stories or themes
    in the ontology.
    """
    def stories(self):
        """
        Iterate over the TOStory objects contained.
        """
        yield from self.story.values()

    def themes(self):
        """
        Iterate over the TOTheme objects contained.
        """
        yield from self.theme.values()

    def astory(self):
        """
        Pick a TOStory object uniformely at random.
        """
        return random.sample(list(self.story.values()), 1)[0]

    def atheme(self):
        """
        Pick a TOTheme object uniformely at random.
        """
        return random.sample(list(self.theme.values()), 1)[0]

    def to_dict(self):
        """
        Present the ontology as a dictionary, suitable for json output.
        """
        return self._impl.to_dict(self)

    def dataframe(self, subset_stories=(), subset_themes=(), implied_themes=False,
        motivation=False, descriptions=False,
    ):
        """
        Present some or all of the ontology as a pandas DataFrame, if pandas is installed.
        """
        import pandas as pd
        headers, data = self._impl.dataframe_records(
            subset_stories, subset_themes, implied_themes, motivation, descriptions,
        )
        return pd.DataFrame(data, columns=headers)

    def print_warnings(self):
        """
        Do basic validation and print warnings to stdout.
        """
        for msg in self.validate():
            print(msg)
        return self

    def write_clean(self):
        """
        Write ontology back to its source in a canonical format.
        """
        self.write(cleaned=True)
