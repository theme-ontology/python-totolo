import totolo


class TestCreation:
    def test_empty(self):
        to = totolo.empty()
        assert len(to) == 0

    def test_remote_head(self):
        to = totolo.remote()
        to.print_warnings()
        assert len(to) > 3

    def test_remote_version_old(self):
        to = totolo.remote.version("v0.3.3")
        to.print_warnings()
        assert len(to) > 3

    def test_remote_version_new(self):
        to = totolo.remote.version("v2023.06")
        to.print_warnings()
        assert len(to) > 3


class TestFunctions:
    def test_theme_ancestors(self):
        to = totolo.files("tests/data/to-2023.07.09.th.txt")
        themes = list(to.theme["love"].ancestors())
        assert set(themes) == set([
            'love',
            'human emotion',
            'individual humans',
            'personal human experience',
            'the human world',
        ])

    def test_theme_descendants(self):
        to = totolo.files("tests/data/to-2023.07.09.th.txt")
        themes = list(to.theme["love"].descendants())
        assert set(themes) == set([
            'love',
            'romantic love',
            'love kindled by danger',
            'impossible love',
            'love at first sight',
            'infatuation',
            'obsessive love',
            'first crush',
            'epic love',
            'forbidden love',
            'secret crush',
            'old-age love',
            'unrequited love',
            'nostalgic love',
            'tragic love',
            'romantic jealousy',
            'familial love',
            'love of a pet',
            'platonic love',
            'sororal love',
            'parental love',
            'paternal love',
            'maternal love',
            'matrimonial love',
            'filial love',
        ])


class TestValidation:
    def test_cycle_warning(self):
        to = totolo.files("tests/data/cycles1.th.txt")
        assert len([msg for msg in to.validate_cycles() if "Cycle:" in msg]) == 1
        to = totolo.files("tests/data/cycles2.th.txt")
        assert len([msg for msg in to.validate_cycles() if "Cycle:" in msg]) == 1
        to = totolo.files("tests/data/cycles3.th.txt")
        assert len([msg for msg in to.validate_cycles() if "Cycle:" in msg]) == 1
