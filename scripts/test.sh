#!/bin/bash
set -euo pipefail
cd `git rev-parse --show-toplevel`
set -o xtrace
pytest --cov-report=xml --cov-fail-under=100 --cov=totolo tests/
pylint totolo
