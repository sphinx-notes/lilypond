=====
Usage
=====

.. _roles:

Roles
=====

.. _lily-role:

The ``lily`` role
-----------------

You can use ``lily`` role to insert a single `LilyPond Music Expression`_ as
inline score.

.. _LilyPond Music Expression: http://lilypond.org/doc/v2.19/Documentation/learning/music-expressions-explained

.. example:: Inline Score
   :style: grid

   :lily:`{c'}` is the first note of the C major scale.

If the score contains `MIDI block`_, the extension will generate audio file
and show a player beside the score:

.. example:: Playable Inline Score
   :style: grid

   :lily:`{c' e' g' } \layout{} \midi{}` is playable.

.. versionadded:: 2.1.0

.. hint::

   Some implementation details to help you debug your music expressions:
   the music expression will be wrapped by a ``\score`` block before passing
   to Lilypond.

   For example, ``:lily:`{c'}``` will be converted to ``\scores { {c'} }``.


.. _directives:

Directives
==========

.. _lily-directive:

The ``lily`` directive
----------------------

The ``lily`` directive is used to insert a complete LilyPond score as
block level element.

.. example::

   .. lily::

      \version "2.20.0"
      \header {
        title = "翼をください, Excerpts"
      }

      \score {
        <<
          \new Staff \relative c' {
              \time 4/4
              \tempo 4 = 70
              r4 r r c8 d                  e8 e f16 e8 d16 (d4) e8 d
              c8 c d16 c8 b16 (b4) b8 g    a4 c8 a g4 c4
              d4 r r r
        }
        >>

        \layout {}
        \midi {}
      }

The directive supports the following options:

:nocrop: (flag)
   Set this option to have scores output to images with appropriate margins and preset size (A4), which is easy for printing. See :example:`Original paper size`.

   .. versionchanged:: 2.0.0

:noaudio: (flag)
   If the score contains `MIDI block`_, Lilypond generates MIDI output files.
   which are converted to audio files by this extension.
   Use this option to disable audio, see :example:`Disable Audio`.

   .. versionchanged:: 2.0.0

   .. _MIDI block: https://lilypond.org/doc/v2.23/Documentation/notation/the-midi-block

:loop: (flag)
   Whethre audio player will automatically seek back to the start upon reaching
   the end of the audio.
   This conflicts with ``noaudio``.
   Example: :example:`Loop`.

   .. versionadded:: 1.2

:transpose: (text)
   Transposing the pitches of score from one to another.
   Pitches are written in `LilyPond Notation`_ and separated in whitespace.
   For example: ``:transpose: g c``, see :example:`Transposing`.

   .. versionadded:: 2.0.0

   .. _LilyPond Notation: http://lilypond.org/doc/Documentation/notation/writing-pitches

:controls: (text, one of the ``top`` or ``bottom``)
   Specify the position of the control bar relative to the score.
   This implies ``audio``. See example :example:`Control Bar at the Top`.

   .. versionadded:: 1.3

The ``lilyinclude`` directive
-----------------------------

The ``lilyinclude`` directive is similar to :ref:`lily-directive`,
except the source of LilyPond are read from file but not contents of directive.

.. example::

   .. lilyinclude:: /_scores/witch-spring.ly

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
 
.. example::

   .. jianpu::

      title=C Major Scale
      1=C
      2/4
      4=60

      1 2 3 4 5 6 7 1'

Options of the directive are same to :ref:`lily-directive`.

The ``jianpuinclude`` directive
-------------------------------

.. versionadded:: 1.6

The ``jianpuinclude`` directive is similar to :ref:`jianpu-directive`,
except the source of Jianpu are read from file but not contents of directive.

.. example::

   .. jianpuinclude:: /_scores/songbie.jp

.. seealso::

    You and download the example LilyPond documentation from here:
    :download:`/_scores/songbie.jp`.

Options of the directive are same to :ref:`lily-directive`.
