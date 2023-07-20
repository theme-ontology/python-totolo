from .core import TOObject, a


class TOKeyword(TOObject):
    keyword = a("")
    capacity = a("")
    motivation = a("")
    notes = a("")

    def __str__(self):
        pm = u" [{}]".format(self.motivation) if self.motivation else ""
        pc = u" <{}>".format(self.capacity) if self.capacity else ""
        pn = u" {{{}}}".format(self.notes) if self.notes else ""
        return u"{}{}{}{}".format(self.keyword, pc, pm, pn)
