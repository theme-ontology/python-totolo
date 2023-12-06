from .impl.entry import TOEntry
from .theme import TOTheme
from .story import TOStory


class TOSet(set):
    def ancestors(self):
        return TOSet(a for o in self for a in o.ancestors())

    def descendants(self):
        return TOSet(a for o in self for a in o.descendants())

    def names(self):
        for x in self:
            if isinstance(x, str):
                yield x
            else:
                yield x.name

    def dataframe(
        self,
        implied_themes=False,
        motivation=False,
        descriptions=False,
    ):
        subset_stories = [x for x in self if isinstance(x, TOStory)]
        subset_themes = [x for x in self if isinstance(x, TOTheme)]
        for obj in self:
            return obj.ontology().dataframe(
                subset_stories=subset_stories,
                subset_themes=subset_themes,
                implied_themes=implied_themes,
                motivation=motivation,
                descriptions=descriptions,
            )
        import totolo  # pylint: disable=cyclic-import
        return totolo.empty().dataframe(
            implied_themes=implied_themes,
            motivation=motivation,
            descriptions=descriptions,
        )

    def ontology(self):
        for x in self:
            if hasattr(x, "ontology"):
                return x.ontology()
        return None


class TODict(dict):
    def __getitem__(self, key):
        if isinstance(key, str):
            return super().__getitem__(key)
        if isinstance(key, TOEntry):
            return super().__getitem__(key.name)
        try:
            obj_iter = iter(key)
        except TypeError as te:
            raise TypeError(
                f"TODict indices must be string, TOEntry, or iterable of the "
                f"same, not {type(key)}"
            ) from te
        return TOSet(self.__getitem__(x) for x in obj_iter)
