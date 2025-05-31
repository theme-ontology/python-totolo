#!/bin/bash
set -euo pipefail
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$BRANCH" != "main" ]]; then
  echo 'Must be on main branch!'
  exit 1
fi
VERSION=`python -c "import totolo; print(totolo.__version__)"`
if [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  git pull
  git tag v$VERSION
  git push origin v$VERSION
else
  echo "unexpected version format: $VERSION"
fi
