import copy

import totolo.lib.textformat

from .core import TOObject, a
from .keyword import TOKeyword


class TOField(TOObject):
    name = a("")
    fieldtype = a("")
    source = a(list)
    parts = a(list)
    frozen = a(False)
    __initialized = False

    def __iadd__(self, other):
        assert isinstance(other, TOField)
        assert self.name == other.name
        assert self.fieldtype == other.fieldtype
        if self.fieldtype == "kwlist":
            self_kws = {p.keyword for p in self.parts}
            for other_part in other.parts:
                if other_part.keyword in self_kws:
                    self.update_kw(
                        other_part.keyword,
                        motivation=other_part.motivation,
                        capacity=other_part.capacity,
                        notes=other_part.notes,
                    )
                else:
                    self.insert_kw(
                        keyword=other_part.keyword,
                        motivation=other_part.motivation,
                        capacity=other_part.capacity,
                        notes=other_part.notes,
                    )
        else:
            self.parts = copy.deepcopy(other.parts)

    def __eq__(self, other):
        if type(self) is not type(other):
            return False
        if self.name != other.name:
            return False
        if self.fieldtype != other.fieldtype:
            return False
        if self.parts != other.parts:
            return False
        return True

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

    def to_obj(self):
        if self.fieldtype == "list":
            return [str(x) for x in self]
        if self.fieldtype == "kwlist":
            return [kw.to_obj() for kw in self]
        return "\n".join(totolo.lib.textformat.remove_wordwrap(part).strip() for part in self)

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

    def setup(self):
        if not self.__initialized and not self.parts and not self.frozen:
            # this used to be done immediately but is now defered for efficiency
            from .parser import TOParser  # pylint: disable=cyclic-import
            TOParser.init_field(self)
            self.__initialized = True
        return self
