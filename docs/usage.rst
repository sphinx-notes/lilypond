=====
Usage
=====

.. TODO: notation

.. _roles:

Roles
=====

.. _lily-role:

The ``lily`` role
-----------------

You can use ``lily`` role to insert short `LilyPond Music Expression`_ as inline
element.

.. _LilyPond Music Expression: http://lilypond.org/doc/v2.19/Documentation/learning/music-expressions-explained

For example:

.. literalinclude:: /_scores/lily-role.txt
    :language: rst

Will be rendered as:

    .. include:: /_scores/lily-role.txt

.. note::

    Role ``lily`` produces a preview image of the music expression (using
    ``-dpreview=#t``). You can still write a long music expression as interpreted text,
    but only the beginning can be shown.

.. _jianpu-role:

The ``jianpu`` role
-------------------

You can use ``jianpu`` role to insert short Jianpu_ (numbered musical notation)
as inline element.

.. hint::

   We use `Silas S. Brown’s Jianpu in Lilypond`_ script to convert Jianpu to
   Lilypond source, so please refer to the page for jianpu Syntax.

.. _Jianpu: https://en.wikipedia.org/wiki/Numbered_musical_notation
.. _Silas S. Brown’s Jianpu in Lilypond: http://ssb22.user.srcf.net/mwrhome/jianpu-ly.html

For example:

.. literalinclude:: /_scores/jianpu-role.txt
    :language: rst

Will be rendered as:

    .. include:: /_scores/jianpu-role.txt

.. _directives:

Directives
==========

.. _lily-directive:

The ``lily`` directive
----------------------

The ``lily`` directive is used to insert a complete LilyPond score as
block level element.

.. literalinclude:: /_scores/lily-directive.txt
    :language: rst

Will be rendered as:

    .. include:: /_scores/lily-directive.txt

The directive supports the following options:

:noheader: (flag)
    Whether to remove the header of score
:nofooter: (flag)
    Whether to remove the footer of score
:noedge: (flag)
    Whether to remove the blank edges of score
:audio: (flag)
    Whether to show a audio player for listen LilyPond-generated MIDI file
:loop: (flag)
    Whethre audio player will automatically seek back to the start upon reaching the end of the audio.
    This implies ``audio``.

    .. versionadded:: 1.2

:transpose: (text)
    Transposing the pitches of score from one to another.
    Pitches are written in `LilyPond Notation`_ and separated in whitespace.
    For example: ``:transpose: c' d'``

    .. _LilyPond Notation: http://lilypond.org/doc/Documentation/notation/writing-pitches

:controls: (text, one of the ``top`` or ``bottom``)
    Specify the position of the control bar relative to the score.
    This implies ``audio``.

    .. versionadded:: 1.3

The ``lilyinclude`` directive
-----------------------------

The ``lilyinclude`` directive is similar to :ref:`lily-directive`,
except the source of LilyPond are read from file but not contents of directive.

.. literalinclude:: /_scores/lilyinclude-directive.txt
   :language: rst

Will be rendered as:

   .. include:: /_scores/lilyinclude-directive.txt

Options of the directive are same to :ref:`lily-directive`.

.. seealso::

    You and download the example LilyPond documentation from here:
    :download:`/_scores/witch-spring.ly`.

.. _jianpu-directive:

The ``jianpu`` directive
------------------------

The ``jianpu`` directive is used to insert a Jianpu_ (numbered musical notation)
score as block level element.

.. hint::

   We use `Silas S. Brown’s Jianpu in Lilypond`_ script to convert Jianpu to
   Lilypond source, so please refer to the page for jianpu Syntax.
   Simply put

Options of the directive are same to :ref:`lily-directive`.
