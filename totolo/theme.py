import html

from .impl.core import sa
from .impl.entry import TOEntry


class TOTheme(TOEntry):
    Description = sa("text", required=True)
    Parents = sa("list")
    Notes = sa("text")
    Examples = sa("text")
    References = sa("list")
    Aliases = sa("list")

    def verbose_description(self):
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

    def html_short_description(self):
        description = str(self.get("Description"))[:256]
        return html.escape(description)

    def html_description(self):
        description = html.escape(str(self.get("Description")))
        examples = html.escape(str(self.get("Examples")).strip())
        aliases = html.escape(str(self.get("Aliases")).strip())
        notes = html.escape(str(self.get("Notes")).strip())
        references = html.escape(str(self.get("References")).strip())
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
        if references:
            description += self.html_references_(references)
        return description

    def _lookup(self):
        try:
            return self.ontology().theme
        except AttributeError:
            return {}
