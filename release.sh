#!/bin/bash
VERSION=`python -c "import totolo; print(totolo.__version__)"`
if [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    git tag v$VERSION
    git push origin v$VERSION
else
  echo "unexpected version format: $VERSION"
fi
