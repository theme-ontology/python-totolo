from collections import OrderedDict

from .core import TOObject, a
from .field import TOField


class TOEntry(TOObject):
    name = a("")
    fields = a(OrderedDict())
    parents = a(set())
    children = a(set())
    source = a([])
    source_location = a("<api>)")
    ontology = a()

    def __str__(self):
        return "{}[{}]".format(
            self.name.encode("ascii", "ignore"),
            len(self.fields)
        )

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.fields[key] = value

    def __delitem__(self, key):
        del self.fields[key]

    def iter_fields(self, reorder=False, skipunknown=False):
        if reorder:
            order = [fn for fn, _ in self.iter_stored()]
        else:
            order = self.fields.keys()
        for fieldname in order:
            field = self.fields.get(fieldname, None)
            if field is not None:
                fieldtype = self.field_type(fieldname)
                if fieldtype != "unknown" or not skipunknown:
                    yield field

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
            yield f"{self.name}: junk in entry header: {junkmsg}"
        for field in self.fields.values():
            if self.field_type(field.name) == "unknown":
                yield f"{self.name}: unknown field '{field.name}'"

    def text_canonical(self):
        lines = [self.name, "=" * len(self.name), ""]
        for field in self.iter_fields(reorder=True, skipunknown=True):
            if self.field_required(field.name) or not field.empty():
                lines.append(field.text_canonical())
                lines.append("")
        return "\n".join(lines)

    def text_original(self):
        lines = [self.name, "=" * len(self.name), ""]
        for field in self.iter_fields(reorder=False, skipunknown=False):
            lines.append(field.text_canonical())
            lines.append("")
        return "\n".join(lines)

    def get(self, fieldname):
        """Get field, returning a frozen default field if it doesn't exist."""
        field = self.fields.get(fieldname, None)
        if field is not None:
            return field
        fieldtype = self.field_type(fieldname)
        return TOField(fieldtype=fieldtype, name=fieldname).freeze()

    def setdefault(self, fieldname):
        """Get field, creating it first if it doesn't exist."""
        field = self.fields.get(fieldname, None)
        if field is not None:
            return field
        fieldtype = self.field_type(fieldname)
        field = TOField(fieldtype=fieldtype, name=fieldname)
        self.fields[fieldname] = field
        return field

    def delete(self, fieldname):
        if fieldname in self.fields:
            del self.fields[fieldname]

    def print(self):
        print(self.text_canonical().strip())

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
