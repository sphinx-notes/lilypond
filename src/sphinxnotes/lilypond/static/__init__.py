"""
sphinxnotes.lilypond.static
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dummpy module for including package_data.

See also ``[tool.setuptools.package-data]`` section of pyproject.toml.

:copyright: Copyright 2025 Shengyu Zhang
:license: BSD, see LICENSE for details.
"""

from pathlib import Path


def dir() -> Path:
    """Get dir of static files."""
    # TODO: use https://docs.python.org/3/library/importlib.resources.html#importlib.resources.files
    return Path(__file__).absolute().parent


def path(fn: str) -> Path:
    """Get file path of static files."""
    return dir() / fn


def read(fn: str) -> str:
    """Get file content of static files."""
    return path(fn).read_text()
