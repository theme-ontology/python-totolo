import totolo
from totolo.collection import TOSet


class TestTOSet:
    def test_toset_strings(self):
        ts = TOSet(['foo', 'bar'])
        assert sorted(ts.names()) == ['bar', 'foo']
        assert ts.ontology() is None

    def test_toset_ontology(self):
        prefix = "tests/data/sample-2023.07.23"
        ontology = totolo.files(prefix)
        toset = ontology.theme[["romantic love"]]
        assert toset.ontology() is ontology

    def test_toset_dataframe(self):
        ontology = totolo.files("tests/data/sample-2023.07.23")
        df = ontology.theme[["electricity"]].dataframe()
        assert len(df) == 3
        subset_stories = [
            s.name for s in ontology.stories() if s.name.startswith("movie:")
        ]
        df = ontology.story[subset_stories].dataframe()
        assert len(df) == 505
        df = ontology.theme[[]].dataframe()
        assert len(df) == 0

    def test_toset_descendants(self):
        prefix = "tests/data/sample-2023.07.23"
        ontology = totolo.files(prefix)
        toset = ontology.theme[["romantic love"]]
        res = ontology.theme[toset.descendants()]
        assert sorted(t.name for t in res) == [
            'epic love', 'first crush', 'forbidden love', 'impossible love',
            'infatuation', 'love at first sight', 'love kindled by danger',
            'nostalgic love', 'obsessive love', 'old-age love',
            'romantic jealousy', 'romantic love', 'secret crush', 'tragic love',
            'unrequited love',
        ]

    def test_toset_ancestors(self):
        prefix = "tests/data/sample-2023.07.23"
        ontology = totolo.files(prefix)
        toset = ontology.theme[["love"]]
        res = ontology.theme[toset.ancestors()]
        assert sorted(t.name for t in res) == [
            'human emotion', 'individual humans', 'love',
            'personal human experience', 'the human world',
        ]

