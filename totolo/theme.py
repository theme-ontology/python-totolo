import html

from .impl.to_object import sa
from .impl.to_entry import TOEntry


class TOTheme(TOEntry):
    """
    A theme in the ontology. The attributes defined with "sa" denote named fields that
    can be accessed using, e.g., `theme.get("Description")`.
    """
    Description = sa("text", required=True)
    Parents = sa("list")
    Notes = sa("text")
    Examples = sa("text")
    References = sa("list")
    Aliases = sa("list")

    def text(self):
        """
        A nicely formatted text representation of the theme.
        """
        return self.text_canonical()

    def ancestors(self) -> 'Iterable[TOTheme]':
        """
        Return a TOCollection set with all themes that contain this story beneeth it in
        the parent-child hierarchy.
        """
        return self.ontology().theme[self.iter_ancestor_names()]

    def descendants(self) -> 'Iterable[TOTheme]':
        """
        Return a TOCollection set with all themes containing this story above  it in the
        parent-child hierarchy.
        """
        return self.ontology().theme[self.iter_descendant_names()]

    def verbose_description(self) -> str:
        """
        A lengthy text description of the story.
        """
        description = str(self.get("Description"))
        examples = str(self.get("Examples")).strip()
        aliases = str(self.get("Aliases")).strip()
        notes = str(self.get("Notes")).strip()
        references = str(self.get("References")).strip()
        if notes:
            description += "\n\nNotes:\n" + notes
        if examples:
            description += "\n\nExamples:\n" + examples
        if aliases:
            description += "\n\nAliases:\n" + aliases
        if references:
            description += self.references_(references)
        return description

    def html_description(self) -> str:
        """
        A lengthy html description of the theme.
        """
        description = html.escape(str(self.get("Description")))
        examples = html.escape(str(self.get("Examples")).strip())
        aliases = html.escape(str(self.get("Aliases")).strip())
        notes = html.escape(str(self.get("Notes")).strip())
        theme_references = html.escape(str(self.get("References")).strip())
        description = '<P class="obj-description"><BR>\n' + description
        description += "</P>\n"
        if notes:
            description += '<P class="obj-description"><b>Notes:</b><BR>\n' + notes
            description += "</P>\n"
        if examples:
            description += '<P class="obj-description"><b>Examples:</b><BR>\n' + examples
            description += "</P>\n"
        if aliases:
            aliases = ', '.join(aliases.split("\n"))
            description += '<P class="obj-description"><b>Aliases:</b><BR>\n' + aliases
            description += "</P>\n"
        if theme_references:
            description += self.html_references_(theme_references)
        return description

    def html_short_description(self) -> str:
        """
        A brief html description of the theme.
        """
        description = str(self.get("Description"))[:256]
        return html.escape(description)

    def subtype(self) -> str:
        """
        Themes have no subtypes.
        """
        return "theme"

    def _lookup(self):
        try:
            return self.ontology().theme
        except AttributeError:
            return {}
