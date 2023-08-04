from .core import TOObject, a


class TOKeyword(TOObject):
    keyword = a("")
    capacity = a("")
    motivation = a("")
    notes = a("")

    def __init__(self, keyword=keyword, capacity=capacity,
                 motivation=motivation, notes=notes):
        self.keyword = keyword
        self.capacity = capacity
        self.motivation = motivation
        self.notes = notes

    def __str__(self):
        capacity = f" <{self.capacity}>" if self.capacity else ""
        motivation = f" [{self.motivation}]" if self.motivation else ""
        notes = f" {{{self.notes}}}" if self.notes else ""
        return f"{self.keyword}{capacity}{motivation}{notes}"
