from .core import TOObject, a
from .keyword import TOKeyword


class TOField(TOObject):
    name = a("")
    fieldtype = a("")
    source = a([])
    data = a([])
    parts = a([])

    def __repr__(self):
        return "{}<{}>[{}]".format(
            type(self).__name__,
            self.name.encode("ascii", "ignore"),
            len(self.data)
        )

    def __str__(self):
        return self.text_canonical_contents()

    def __iter__(self):
        for part in self.iter_parts():
            yield part

    def iter_parts(self):
        """
        Iterater over components in the data of this field.
        """
        for part in self.parts:
            yield part

    def text_canonical_contents(self):
        """
        Returns:
            A text blob representing the contents of this field in its canonical format.
        """
        parts = [str(x) for x in self.iter_parts()]
        return u'\n'.join(parts)

    def text_canonical(self):
        """
        Returns:
            A text blob representing this field in its canonical format.
        """
        parts = [u":: {}".format(self.name)]
        parts.extend(str(x) for x in self.iter_parts())
        return u'\n'.join(parts)

    def delete(self, kw):
        """
        Delete a keyword.
        """
        fieldtype = self.fieldconfig.get("type", "blob")
        todelete = set()
        if fieldtype == "kwlist":
            for idx, part in enumerate(self.parts):
                if part.keyword == kw:
                    todelete.add(idx)
        self.parts = [p for idx, p in enumerate(self.parts) if idx not in todelete]
        return min(todelete) if todelete else len(self.parts)

    def update(self, kw, keyword=None, motivation=None, capacity=None, notes=None):
        """
        Update keyword data.
        """
        fieldtype = self.fieldconfig.get("type", "blob")
        if fieldtype == "kwlist":
            for part in self.parts:
                if part.keyword == kw:
                    if keyword is not None:
                        part.keyword = keyword
                    if motivation is not None:
                        part.motivation = motivation
                    if capacity is not None:
                        part.capacity = capacity
                    if notes is not None:
                        part.notes = notes

    def insert(self, idx=None, keyword="", motivation="", capacity="", notes=""):
        """
        Insert a new keyword at location idx in the list.
        If idx is None, append.
        """
        if idx is None:
            idx = len(self.parts)
        self.parts.insert(
            idx,
            TOKeyword(
                keyword,
                capacity=capacity,
                motivation=motivation,
                notes=notes
            )
        )
