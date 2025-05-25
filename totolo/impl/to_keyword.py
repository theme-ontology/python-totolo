from collections import OrderedDict

from .to_object import TOObject


class TOKeywordBase(TOObject):
    def __init__(self, keyword="", capacity="", motivation="", notes=""):
        self.keyword = keyword
        self.capacity = capacity
        self.motivation = motivation
        self.notes = notes

    def __str__(self):
        capacity = f" <{self.capacity}>" if self.capacity else ""
        motivation = f" [{self.motivation}]" if self.motivation else ""
        notes = f" {{{self.notes}}}" if self.notes else ""
        return f"{self.keyword}{capacity}{motivation}{notes}"

    def to_obj(self):
        ret = [
            ("name", self.keyword),
            ("motivation", self.motivation),
            ("capacity", self.capacity),
        ]
        if self.notes:
            ret.append(("notes", self.notes))
        return OrderedDict(ret)
