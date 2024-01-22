from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import totolo.lib.log as log


def test_logging():
    components = [
        "info",
        "warning",
        "error",
        "critical",
    ]

    stdout = StringIO()
    stderr = StringIO()
    logged = StringIO()

    logger = log._logger
    stream_handler = log.logging.StreamHandler(logged)
    logger.addHandler(stream_handler)

    with redirect_stderr(stderr):
        with redirect_stdout(stdout):
            for part in components:
                getattr(log, part)(f"log {part}")

    assert stdout.getvalue() == ""
    assert stderr.getvalue() == ""
    logged_lines = logged.getvalue().splitlines()
    for idx, part in enumerate(components):
        logged_lines[idx].endswith(f"log {part}")
