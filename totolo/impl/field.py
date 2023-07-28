from .core import TOObject, a
from .keyword import TOKeyword


class TOField(TOObject):
    name = a("")
    fieldtype = a("")
    source = a([])
    data = a([])
    parts = a([])
    frozen = a(False)

    def __setattr__(self, name, value):
        if name != "frozen":
            self.assert_mutable()
        super().__setattr__(name, value)

    def __repr__(self):
        tname = type(self).__name__
        name = self.name.encode("ascii", "ignore")
        ndata = len(self.data)
        return f"{tname}<{name}>[{ndata}]"

    def __str__(self):
        return self.text_canonical_contents()

    def __iter__(self):
        for part in self.iter_parts():
            yield part

    def freeze(self):
        if not self.frozen:
            self.source = tuple(self.source)
            self.data = tuple(self.data)
            self.parts = tuple(self.parts)
            self.frozen = True
        return self

    def assert_mutable(self):
        if getattr(self, "frozen", False):
            raise AttributeError(
                "Object is frozen, indicating it is detached from an ontology.")
        return True

    def str(self):
        return str(self)

    def list(self):
        return list(self.parts)

    def empty(self):
        return not any(self.parts)

    def iter_parts(self):
        for part in self.parts:
            yield part

    def text_canonical_contents(self):
        parts = [str(x) for x in self.iter_parts()]
        return "\n".join(parts)

    def text_canonical(self):
        parts = [f":: {self.name}"]
        parts.extend(str(x) for x in self.iter_parts())
        return "\n".join(parts)

    def text_original(self):
        return "\n".join(self.source)

    def delete_kw(self, keyword):
        self.assert_mutable()
        fieldtype = self.fieldtype
        todelete = set()
        if fieldtype == "kwlist":
            for idx, part in enumerate(self.parts):
                if part.keyword == keyword:
                    todelete.add(idx)
        self.parts = [p for idx, p in enumerate(self.parts) if idx not in todelete]
        return len(todelete)

    def update_kw(self, match_keyword, keyword=None,
                  motivation=None, capacity=None, notes=None):
        self.assert_mutable()
        assert self.fieldtype == "kwlist"
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
        self.assert_mutable()
        assert self.fieldtype == "kwlist"
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
