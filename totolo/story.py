import re

from .impl.core import sa
from .impl.entry import TOEntry


class TOStory(TOEntry):
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

    def iter_theme_entries(self):
        """
        Yield (weight, TOKeyword) pairs. TOKeyword contains the comment and other
        metadata associated with a theme entry in a story.
        """
        for weight in ["Choice Themes", "Major Themes", "Minor Themes", "Not Themes"]:
            field = self.get(weight)
            if field:
                for part in field.iter_parts():
                    yield weight, part

    def iter_themes(self):
        """
        Iterate over the theme objects associated with this story object.
        """
        if not getattr(self, "ontology", None):
            raise RuntimeError(
                "Story must be associated with an ontology to look up themes.")
        to = self.ontology()
        for weight, part in self.iter_theme_entries():
            theme = to.theme[part.keyword]
            yield weight, theme

    @property
    def date(self):
        """
        Return the date entry as verbatim it is recorded in the text file.
        """
        return self.get("Date").text_canonical_contents().strip()

    @property
    def year(self):
        """
        Returns the year of the story, or the earliest year for a collection.
        A positive number is the year AD.
        A negative number is the year BC.
        Zero indicates that the the information is missing (there is no year zero in
        AD/BC notation). Dates can be entered in a variety of ways but the year should
        always be present. If this function returns zero for a story the story's data
        entry is considered to be faulty.
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
    def sid(self):
        return self.name

    @property
    def title(self):
        return self.get("Title").text_canonical_contents().strip()

    def verbose_description(self):
        """
        A description that combines various other fields, including Notes, Examples,
        Aliases, and References.
        """
        description = str(self.get("Description"))
        references = str(self.get("References")).strip()
        if references:
            description += "\n\nReferences:\n"
            for line in references.split("\n"):
                line = line.strip()
                if line:
                    description += line + "\n"
        return description

    def html_description(self):
        """
        Turn the verbose description into html.
        """
        import html
        description = html.escape(str(self.get("Description")))
        references = html.escape(str(self.get("References")).strip())
        description = '<P class="obj-description"><BR>\n' + description
        description += "</P>\n"
        if references:
            description += '<P class="obj-description"><b>References:</b><BR>\n'
            for line in references.split("\n"):
                line = line.strip()
                if line:
                    aline = '<A href="{}">{}</A>'.format(line, line)
                    description += aline + "\n"
            description += "</P>\n"
        return description

    def html_short_description(self):
        """
        A limited length short description without embelishments like "references".
        """
        import html
        description = str(self.get("Description"))[:256]
        return html.escape(description)

    def _lookup(self):
        try:
            return self.ontology().story
        except AttributeError:
            return {}
