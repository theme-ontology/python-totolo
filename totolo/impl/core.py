from collections import OrderedDict
from copy import deepcopy


class TOAttr:
    def __init__(self, default=""):
        self.default = default


class TOStoredAttr(TOAttr):
    def __init__(self, datatype="blob", default="", required=False):
        super().__init__(default)
        self.datatype = datatype
        self.required = required


class TOObjectMeta(type):
    def __new__(meta, name, bases, attr):
        to_attrs = OrderedDict()
        for base in bases:
            for key, value in getattr(base, "_to_attrs", {}).items():
                if key not in attr:
                    to_attrs[key] = value
        for key, value in list(attr.items()):
            if isinstance(value, TOAttr):
                to_attrs[key] = value
                del attr[key]
        attr["_to_attrs"] = to_attrs
        return super().__new__(meta, name, bases, attr)

    def __call__(cls, *args, **kwargs):
        self = super().__call__(*args, **kwargs)
        for key, value in self._to_attrs.items():
            if not hasattr(self, key):
                setattr(self, key, deepcopy(value.default))
        return self

    @classmethod
    def __prepare__(mcls, _cls, _bases):
        return OrderedDict()


def a(*args, **kwargs):
    return TOAttr(*args, **kwargs)


def sa(*args, **kwargs):
    return TOStoredAttr(*args, **kwargs)


class TOObject(metaclass=TOObjectMeta):
    def __init__(self, *args, **kwargs):
        super().__init__()
        for arg, key in zip(args, self._to_attrs.keys()):
            setattr(self, key, arg)
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.get_attr = self._to_attrs.get

    def iter_attrs(self):
        yield from self._to_attrs.items()

    def iter_stored(self):
        for key, value in self.iter_attrs():
            if isinstance(value, TOStoredAttr):
                yield key, value

    def field_type(self, key):
        key = key.replace(" ", "_")
        try:
            return self.get_attr(key).datatype
        except (KeyError, AttributeError) as _e:
            return "unknown"

    def __str__(self):
        return "[toobject]"

    def __repr__(self):
        return f'{type(self).__name__}<{str(self)}>'

    def __getitem__(self, key):
        key = key.replace(" ", "_")
        attr = self._to_attrs.get(key, None)
        if isinstance(attr, TOStoredAttr):
            return getattr(self, key)
        raise KeyError(f"{type(self).__name__} has no stored attribute {key}")

    def __setitem__(self, key, value):
        key = key.replace(" ", "_")
        attr = self._to_attrs.get(key, None)
        if isinstance(attr, TOStoredAttr):
            return setattr(self, key, value)
        raise KeyError(f"{type(self).__name__} has no stored attribute {key}")
