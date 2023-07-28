from collections import OrderedDict
from copy import deepcopy


class TOAttr:
    def __init__(self, default="", private=False):
        self.default = default
        self.private = private

    def __str__(self):
        tname = self.__class__.__name__
        return f"{tname}({self.default})"


class TOStoredAttr(TOAttr):
    def __init__(self, datatype="blob", default=None, required=False):
        if default is None:
            default = [] if "list" in datatype else ""
        super().__init__(default, True)
        self.datatype = datatype
        self.required = required

    def __str__(self):
        tname = self.__class__.__name__
        return f"{tname}<{self.datatype}>({self.default})"


class TOObjectMeta(type):
    def __new__(mcs, name, bases, attr):
        to_attrs = OrderedDict()
        for base in bases:
            for key, value in getattr(base, "_to_attrs", {}).items():
                if key not in attr:
                    to_attrs[key] = value
        for key, value in list(attr.items()):
            if isinstance(value, TOStoredAttr):
                nkey = key.replace("_", " ")
                to_attrs[nkey] = value
                del attr[key]
            elif isinstance(value, TOAttr):
                to_attrs[key] = value
                del attr[key]
        attr["_to_attrs"] = to_attrs
        return super().__new__(mcs, name, bases, attr)

    def __call__(cls, *args, **kwargs):
        self = super().__call__(*args, **kwargs)
        for key, value in self._to_attrs.items():
            if not value.private and not hasattr(self, key):
                setattr(self, key, deepcopy(value.default))
        return self

    @classmethod
    def __prepare__(mcs, _cls, _bases):
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
        for key, value in self._to_attrs.items():
            yield key, value

    def iter_stored(self):
        for key, value in self.iter_attrs():
            if isinstance(value, TOStoredAttr):
                yield key, value

    def field_type(self, key):
        try:
            return self.get_attr(key).datatype
        except (KeyError, AttributeError) as _e:
            return "unknown"

    def field_required(self, key):
        try:
            return self.get_attr(key).required
        except (KeyError, AttributeError) as _e:
            return False

    def __str__(self):
        return "[TOObject]"

    def __repr__(self):
        return f'{type(self).__name__}<{str(self)}>'
