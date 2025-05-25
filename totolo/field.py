import totolo.lib.textformat

from .impl.to_field import TOFieldBase
from .keyword import TOKeyword


class TOField(TOFieldBase):
    def text_canonical_contents(self):
        """
        Return text representation of the contents of this field in canonical format.
        The heading is not included.
        """
        text = "\n".join(str(x) for x in self)
        if self.fieldtype == "text":
            text = totolo.lib.textformat.add_wordwrap(text).strip()
        return text

    def text_canonical(self):
        """
        Return text representation of this field in canonical format, including heading.
        """
        parts = [f":: {self.name}", self.text_canonical_contents()]
        return "\n".join(parts)

    def text_original(self):
        return "\n".join(self.source)

    def delete_kw(self, keyword):
        assert self.mutable().setup().fieldtype == "kwlist"
        todelete = set()
        for idx, part in enumerate(self.parts):
            if part.keyword == keyword:
                todelete.add(idx)
        self.parts = [p for idx, p in enumerate(self.parts) if idx not in todelete]
        return len(todelete)

    def update_kw(self, match_keyword, keyword=None,
                  motivation=None, capacity=None, notes=None):
        assert self.mutable().setup().fieldtype == "kwlist"
        for part in self.parts:
            if part.keyword == match_keyword:
                if keyword is not None:
                    part.keyword = keyword
                if motivation is not None:
                    part.motivation = motivation
                if capacity is not None:
                    part.capacity = capacity
                if notes is not None:
                    part.notes = notes

    def insert_kw(self, idx=None, keyword="", motivation="", capacity="", notes=""):
        assert self.mutable().setup().fieldtype == "kwlist"
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

    def find_kw(self, match_keyword):
        for part in self.parts:
            if part.keyword == match_keyword:
                return part
        return None
