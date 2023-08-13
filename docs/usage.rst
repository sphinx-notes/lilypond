=====
Usage
=====

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

:nocrop: (flag)
   Set this option to have scores output to images with appropriate margins and preset size (A4), which is easy for printing. See :ref:`example-nocrop`.

   .. versionchanged:: 2.0.0

:noaudio: (flag)
   If the score contains `MIDI block`_, Lilypond generates MIDI output files.
   which are converted to audio files by this extension.
   Use this option to disable audio, see :ref:`example-noaudio`

   .. versionchanged:: 2.0.0

   .. _MIDI block: https://lilypond.org/doc/v2.23/Documentation/notation/the-midi-block

:loop: (flag)
   Whethre audio player will automatically seek back to the start upon reaching
   the end of the audio.
   This conflicts with ``noaudio``.

   .. versionadded:: 1.2

:transpose: (text)
   Transposing the pitches of score from one to another.
   Pitches are written in `LilyPond Notation`_ and separated in whitespace.
   For example: ``:transpose: c' d'``

   .. versionadded:: 2.0.0

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

.. versionadded:: 1.6

The ``jianpu`` directive is used to insert a Jianpu_
(Numbered Musical Notation, 简谱) score as block level element.

.. hint::

   The syntax of Jianpu is defined by `Silas S. Brown`_ and we use his
   `jianpu-ly`_ script to convert Jianpu source code to Lilypond source
   code, and finally engraving a music score.

.. _Jianpu: https://en.wikipedia.org/wiki/Numbered_musical_notation
.. _Silas S. Brown:  https://ssb22.user.srcf.net/
.. _jianpu-ly: http://ssb22.user.srcf.net/mwrhome/jianpu-ly.html

.. literalinclude:: /_scores/jianpu-directive.txt
    :language: rst

Will be rendered as:

   .. include:: /_scores/jianpu-directive.txt

Options of the directive are same to :ref:`lily-directive`.

The ``jianpuinclude`` directive
-------------------------------

.. versionadded:: 1.6

The ``jianpuinclude`` directive is similar to :ref:`jianpu-directive`,
except the source of Jianpu are read from file but not contents of directive.

.. literalinclude:: /_scores/jianpuinclude-directive.txt
   :language: rst

Will be rendered as:

   .. include:: /_scores/jianpuinclude-directive.txt

.. seealso::

    You and download the example LilyPond documentation from here:
    :download:`/_scores/songbie.jianpu`.

Options of the directive are same to :ref:`lily-directive`.
