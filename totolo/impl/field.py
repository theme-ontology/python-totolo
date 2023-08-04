import totolo.lib.textformat

from .core import TOObject, a
from .keyword import TOKeyword


class TOField(TOObject):
    name = a("")
    fieldtype = a("")
    source = a(list)
    parts = a(list)
    frozen = a(False)

    def __setattr__(self, name, value):
        if name != "frozen":
            self.mutable()
        super().__setattr__(name, value)

    def __repr__(self):
        self.setup()
        tname = type(self).__name__
        name = self.name.encode("ascii", "ignore")
        ndata = len(self.parts)
        return f"{tname}<{name}>[{ndata}]"

    def __str__(self):
        return self.text_canonical_contents()

    def __iter__(self):
        yield from self.setup().parts

    def freeze(self):
        if not self.frozen:
            self.setup()
            self.source = tuple(self.source)
            self.parts = tuple(self.parts)
            self.frozen = True
        return self

    def mutable(self):
        if getattr(self, "frozen", False):
            raise AttributeError(
                "Object is frozen, indicating it is detached from an ontology.")
        return self

    def str(self):
        return str(self)

    def empty(self):
        return not any(self.setup().parts)

    def text_canonical_contents(self):
        text = "\n".join(str(x) for x in self)
        if self.fieldtype == "text":
            text = totolo.lib.textformat.add_wordwrap(text).strip()
        return text

    def text_canonical(self):
        parts = [f":: {self.name}"]
        parts.extend(str(x) for x in self)
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

    def setup(self):
        if not self.parts and not self.frozen:
            # this used to be done immediately but is now defered for efficiency
            from .parser import TOParser  # pylint: disable=cyclic-import
            TOParser.init_field(self)
        return self
