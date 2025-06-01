import html
import re

from .impl.to_containers import TOSet
from .impl.to_entry import TOEntry
from .impl.to_object import sa


class TOStory(TOEntry):
    """
    A story in the ontology. The attributes defined with "sa" denote named fields that
    can be accessed using, e.g., `story.get("Title")`.
    """
    Title = sa("text", required=True)
    Date = sa("date", required=True)
    Description = sa("text")
    Authors = sa("blob")
    Variation = sa("blob")
    References = sa("list")
    Ratings = sa("list")
    Collections = sa("list")
    Component_Stories = sa("list")
    Related_Stories = sa("list")
    Choice_Themes = sa("kwlist")
    Major_Themes = sa("kwlist")
    Minor_Themes = sa("kwlist")
    Not_Themes = sa("kwlist")
    Other_Keywords = sa("kwlist")

    @property
    def date(self) -> str:
        """
        Return the date entry as verbatim it is recorded in the text file.
        """
        return self.get("Date").text_canonical_contents().strip()

    @property
    def year(self) -> int:
        """
        Returns the year of the story, or the earliest year for a collection.
         - A positive number is the year AD.
         - A negative number is the year BC.
         - Zero for any story the ontology is faulty.
        The year is a required component of any story entry as it anchors it somewhere
        in human history, even if just approximately.
        """
        date = self.date
        yearmatch = re.match("\\d+", date)
        if not yearmatch:
            return 0
        year = int(yearmatch.group())
        if "bc" in date.lower():
            year *= -1
        return year

    @property
    def title(self) -> str:
        """
        Shorthand for the story's title.
        """
        return self.get("Title").text_canonical_contents().strip()

    def text(self):
        """
        A nicely formatted text representation of the story.
        """
        return self.text_canonical()

    def ancestors(self) -> 'Iterable[TOStory]':
        """
        Return a TOCollection set with all stories containing this story as a component.
        """
        return self.ontology().story[self.iter_ancestor_names()]

    def descendants(self) -> 'Iterable[TOStory]':
        """
        Return a TOCollection set with all stories contained as a component of this story.
        """
        return self.ontology().story[self.iter_descendant_names()]

    def iter_theme_entries(self) -> 'Iterable[tuple(str, TOKeyword)]':
        """
        Yield (weight, TOKeyword) pairs. A TOKeyword has at least the attributes
        "keyword" (the theme name), "capacity" (triangle bracket entry) and "motivation"
        (square bracket entry), i.e., metadata associated with a theme entry in a story.
        """
        for weight in ["Choice Themes", "Major Themes", "Minor Themes", "Not Themes"]:
            field = self.get(weight)
            for part in field or ():
                yield weight, part

    def iter_themes(self) -> 'Iterable[tuple(str, TOTheme)]':
        """
        Iterate over (weight, TOTheme) associated with this story object. To access motivations
        etc. for an entry, use "iter_theme_entries" instead.
        """
        ontology = self.ontology()
        if ontology is None:
            raise RuntimeError("Story must be associated with an ontology to look up themes.")
        for weight, part in self.iter_theme_entries():
            theme = ontology.theme[part.keyword]
            yield weight, theme

    def themes(self, weight=None):
        """
        Return a list of all themes by weight.
        :param weight: "choice", "major", or "minor". If None, admit all.
        """
        weight = weight or []
        if isinstance(weight, str):
            weight = [weight]
        def shorten(w):
            return w.split(" ", 1)[0].lower()
        weight = {shorten(w) for w in weight}
        return TOSet(
            t for w, t in self.iter_themes()
            if not weight or shorten(w) in weight
        )

    def verbose_description(self) -> str:
        """
        A lengthy text description of the story.
        """
        description = str(self.get("Description"))
        references = str(self.get("References")).strip()
        if references:
            description += self.references_(references)
        return description

    def html_description(self) -> str:
        """
        A lengthy html description of the story.
        """
        description = html.escape(str(self.get("Description")))
        story_references = html.escape(str(self.get("References")).strip())
        description = '<P class="obj-description"><BR>\n' + description
        description += "</P>\n"
        if story_references:
            description += self.html_references_(story_references)
        return description

    def html_short_description(self) -> str:
        """
        A short html description of the story.
        """
        description = str(self.get("Description"))[:256]
        return html.escape(description)

    def subtype(self) -> str:
        """
        Return whether object represents a "collection" or a general "story".
        """
        if self.name.startswith("Collection: "):
            return "collection"
        return "story"

    def _lookup(self):
        try:
            return self.ontology().story
        except AttributeError:
            return {}
