import sys
from unittest.mock import patch

import totolo
import totolo.util.help


class TestHelp:
    def test_help(self):
        testargs = ["help"]
        with patch.object(sys, 'argv', testargs):
            totolo.util.help.main()
