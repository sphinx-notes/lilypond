"""
    sphinxnotes.lilypond.binding
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Jianpu to Lilypond transformer.
    This module wraps https://github.com/ssb22/jianpu-ly

    .. seealso:: https://github.com/ssb22/jianpu-ly/issues/15

    :copyright: Copyright ©2020 by Shengyu Zhang.
    :license: BSD, see LICENSE for details.
"""

import importlib
from . import jianpu_ly

class Error(Exception):
    pass

def to_lilypond(jp: str) -> str:
    """
    Convert Jianpu source to Lilypond source.

    .. note::

       Due to https://github.com/ssb22/jianpu-ly/issues/35, we have to
       reload jianpu-ly module every time.
    """
    try:
        return jianpu_ly.process_input(jp)
    except Exception as e:
        raise Error(e) from e
    finally:
        importlib.reload(jianpu_ly)
