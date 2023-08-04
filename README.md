[![PyPI version](https://badge.fury.io/py/totolo.svg)](https://badge.fury.io/py/totolo)
[![codecov](https://codecov.io/gh/theme-ontology/python-totolo/branch/main/graph/badge.svg?token=1Z39E9IE2W)](https://codecov.io/gh/theme-ontology/python-totolo)
[![Life cycle](https://img.shields.io/badge/lifecycle-stable-brightgreen.svg)](https://lifecycle.r-lib.org/articles/stages.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
 
# Python Totolo

This repository contains a Python package, totolo, for working with data from the Theme Ontology [theming repository](https://github.com/theme-ontology/theming/).


## Installation

Install from PyPi:

```
pip install totolo
```

Or clone this repository and copy the `totolo` directory wherever you need it. No dependencies are required.


## Basic Usage

```python
#: get the latest main branch version of the ontology
>>> ontology = totolo.remote()
>>> print(ontology)
<2945 themes, 4475 stories>

#: write it or read it locally
>>> ontology.write("/home/mo/themes")
>>> ontology = totolo.files("/home/mo/themes")
>>> print(ontology)
<2945 themes, 4475 stories>
```

Explore the themes:

```python
#: go over all the themes and find the ones you want
>>> for theme in ontology.themes():
...     if "romantic love" in theme.name:
...         print(theme)
# b'personal freedom vs. romantic love'[3]
# b'romantic love'[3]

#: check the definition of a theme
>>> love = ontology.theme["love"]
>>> love.print()
(...)
```

Explore the stories:

```python
>>> for weight, theme in story.iter_themes():
...     print(f"{weight:<15} {theme.name}")
```

``` 
Choice Themes   betrayal
Choice Themes   the lust for power
(...)
```

Convert it to a pandas dataframe:

```python
>>> df = ontology.dataframe()
>>> df
```

```
                                 story_id             title        date                      theme        weight
0                 theamericanshortstory01  The Music School        1974      human self-reflection  Major Themes
1                 theamericanshortstory01  The Music School        1974                     murder  Major Themes
...                                   ...               ...         ...                        ...           ...
52453  videogame: Final Fantasy VI (1994)  Final Fantasy VI  1994-04-02  feral children in society  Minor Themes
52454  videogame: Final Fantasy VI (1994)  Final Fantasy VI  1994-04-02             father and son  Minor Themes

[52455 rows x 5 columns]
```

## Getting Help

If you encounter a bug, please file a minimal reproducible example on
[GitHub issues](https://github.com/theme-ontology/python-totolo/issues/). For
feature requests and other matters, please post on the [GitHub discussions
board](https://github.com/theme-ontology/python-totolo/discussions/).

## License

All code in this repository is published with the
[MIT](https://opensource.org/license/mit/) license.

## Code Test Coverage

[![codecov](https://codecov.io/gh/theme-ontology/python-totolo/branch/main/graphs/icicle.svg?token=1Z39E9IE2W)](https://codecov.io/gh/theme-ontology/python-totolo)

