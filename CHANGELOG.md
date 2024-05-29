# Changelog

## Origin
Still to come...

## Versions

### v1.0.0 - The Origin
- Created the `node.py` file
- Added the `Node` class
- Allowed it to have children
- Allowed it to reference a parent
- Allowed it to have references to its siblings.
- Added a search function to search the tree for a given node by kwargs.
- Added an `__init__` library.
- Typechecked using `assert` only.

### v1.0.1 - Some Extra Work
- Removed the ability to reference a parent in the `__init__`
- Added a node cap and checks to remove the node cap
- Added the ability to reference children as attributes using `setattr()`
- Added naming protection so a name is in Pythonic syntax
- Added some basic protection against adding a node higher than the current node as a child using tiers.
- Privatised some methods by prefixing them with `__`
- Added `@property` headers for the `siblings`, `children` and `parent` attributes.
- Gave it a "file path" representation in the `__repr__` file.
- Added a node collection system using recursion
    - This is accessed using `.collect()` on the node to collect all of its children.

### v1.1.0 - Learning from the Better
- Updated the search functions to include multiple different types of searching:
    - Searching using a function (like a `lambda`)
    - Searching for attributes on the node _itself_
    - Searching for attributes on the node's _value_

- Included three new files:
    - a `README.md` file for project description
    - a `CHANGELOG.md` file for changelogs
    - a `pyproject.toml` file for PyPI

- Dropped the `utils.py` file and integrated the functions with the `Node` class itself.
- Replaced all the assertations (places I used `assert`) with `isinstance()` checks and raising appropriate errors.
- Created `errors.py` to hold all appropriate errors and separate them from the `node.py` code.
- Turned the original `search_for()` method into a dunder method.
- Created a surface-level `search_for()` method which handles type-checking
    - If the type checks were in the recursive function
      then they would be checked continuously over and
      over again which could warrant performance issues.

- Fixed the language of the docstrings to be more formal.