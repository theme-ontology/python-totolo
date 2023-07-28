from totolo.lib.textformat import add_wordwrap, remove_wordwrap


def test_remove_wordwrap():
    text = """
Lorem ipsum dolor sit
amet, consectetur adipiscing elit, sed
do eiusmod tempor incididunt ut
labore et dolore magna aliqua.

Ut enim ad minim veniam, quis nostrud

exercitation ullamco laboris nisi ut
aliquip ex ea commodo consequat.


Duis aute irure dolor in reprehenderit in
voluptate velit esse cillum dolore eu fugiat
nulla pariatur. Excepteur sint occaecat cupidatat
non proident, sunt in culpa qui officia
deserunt mollit anim id est laborum.
    """.strip()
    text_out = remove_wordwrap(text)
    print(text_out)
    words = text.split()
    words_out = text_out.split()
    assert words == words_out


def test_add_wordwrap():
    text = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod "
        "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, "
        "quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo "
        "consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse "
        "cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non "
        "proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    )
    text_out = add_wordwrap(text)
    print(text_out)
    words = text.split()
    words_out = text_out.split()
    assert words == words_out
