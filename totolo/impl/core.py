from collections import OrderedDict


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
            default = list if "list" in datatype else ""
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
        attr["_to_attrs_public"] = {
            k: v for k, v in to_attrs.items() if not v.private
        }
        return super().__new__(mcs, name, bases, attr)

    def __call__(cls, *args, **kwargs):
        self = super().__call__(*args, **kwargs)
        target = self.__dict__
        for key, value in self._to_attrs_public.items():
            if not key in target:
                if callable(value.default):
                    target[key] = value.default()
                else:
                    target[key] = value.default
        return self

    @classmethod
    def __prepare__(mcs, _cls, _bases):
        return OrderedDict()


def a(*args, **kwargs):
    return TOAttr(*args, **kwargs)


def sa(*args, **kwargs):
    return TOStoredAttr(*args, **kwargs)


class TOObject(metaclass=TOObjectMeta):
    def __init__(self, **kwargs):
        super().__init__()
        self.__dict__.update(kwargs)

    def __eq__(self, other):
        if {k for k, _ in self.iter_attrs()} != {k for k, _ in other.iter_attrs()}:
            return False
        for key, attr in self.iter_attrs():
            if not attr.private:
                if getattr(self, key) != getattr(other, key):
                    return False
        return True

    def get_attr(self, key):
        return self._to_attrs.get(key)

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
