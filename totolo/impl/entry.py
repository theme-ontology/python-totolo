from .core import TOObject, a
from .field import TOField


class TOEntry(TOObject):
    name = a("")
    fields = a([])
    parents = a(set())
    children = a(set())
    source = a([])
    source_location = a("<api>)")

    def __str__(self):
        return "{}[{}]".format(
            self.name.encode("ascii", "ignore"),
            len(self.fields)
        )

    def iter_fields(self, reorder=False, skipunknown=False):
        lu = {f.name: f for f in self.fields}
        if reorder:
            order = [f for f, _ in self.iter_stored() if f in lu]
        else:
            order = [f.name for f in self.fields]
        for fieldname in order:
            field = lu.get(fieldname, None)
            if field:
                fieldtype = self.field_type(fieldname)
                if fieldtype != "unknown" or not skipunknown:
                    yield field

    def _lookup(self):
        return {}

    def _dfs(self, attr, lookup):
        visited = set()
        pending = [self.name]
        visited.update(pending)
        while pending:
            name = pending.pop()
            yield name
            item = lookup[name]
            for nitem in getattr(item, attr):
                if nitem not in visited:
                    pending.append(nitem)
                    visited.add(nitem)

    def ancestors(self):
        yield from self._dfs("parents", self._lookup())

    def descendants(self):
        yield from self._dfs("children", self._lookup())

    def validate(self):
        junklines = []
        for idx, line in enumerate(self.source):
            if idx > 1:
                if line.startswith("::"):
                    break
                elif line.strip():
                    junklines.append(line)
        if junklines:
            junkmsg = '/'.join(junklines)
            if len(junkmsg) > 13:
                junkmsg = junkmsg[:10] + "..."
            yield u"{}: junk in entry header: {}".format(self.name, junkmsg)
        for field in self.fields:
            if self.field_type(field.name) == "unknown":
                yield u"{}: unknown field '{}'".format(self.name, field.name)

    def text_canonical(self):
        lines = [self.name, "=" * len(self.name), ""]
        for field in self.iter_fields(reorder=True, skipunknown=True):
            lines.append(field.text_canonical())
            lines.append("")
        return "\n".join(lines)

    def get(self, fieldname):
        for field in self.fields:
            if field.name == fieldname:
                return field
        fieldtype = self.field_type(fieldname)
        self.fields.append(TOField(fieldtype=fieldtype, name=fieldname))
        return self.fields[-1]

    def print(self):
        print(self.text_canonical().strip())
