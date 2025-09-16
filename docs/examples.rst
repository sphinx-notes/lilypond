========
Examples
========

The LilyPond documentation used in example can be downloaded here:
:download:`/_scores/minuet-in-g.ly`.

Original paper size
===================

.. example:: _

   .. lilyinclude:: /_scores/minuet-in-g.ly
      :nocrop:

Disable Audio
=============

.. example:: _

   .. lilyinclude:: /_scores/minuet-in-g.ly
      :noaudio:

Transposing
===========

.. example:: _

   .. lilyinclude:: /_scores/minuet-in-g.ly
      :transpose: g c

Multiple Pages
==============

.. example:: _

   .. lilyinclude:: /_scores/alice.ly

Loop
====

.. example:: _

   .. lilyinclude:: /_scores/minuet-in-g.ly
      :loop:

.. versionadded:: 1.2

Control Bar at the Top
======================

.. example:: _

   .. lilyinclude:: /_scores/minuet-in-g.ly
      :controls: top

.. versionadded:: 1.3

Jianpu (Numbered Musical Notation)
==================================

.. example:: _

   .. jianpu::

      title=C Major Scale
      1=C
      4=60
      2/4

      1 2 3 4 5 6 7 1'

.. seealso:: :ref:`jianpu-directive`.

.. versionadded:: 1.5

Jianpu (Change Chords into Roman Numerals)
==========================================

.. example:: _

   .. jianpu::

      NoBarNums % break heigth of chore names
      ChordsRoman

      title=送别
      4=80
      1=A
      4/4

      chords= a1 d2 a2 a1 e:7 a1 d2 a2 a1 e:7 d1 e:7 a2 d2 a2 e:7 a1 d2 a2 e:7 a1

      5 q3 q5 1' -
      6  q1' q6 5 -
      5 q1 q2 3 q2 q1
      2  - - 0
      \break

      5 q3 q5 1'. q7
      6 1' 5 -
      5 q2 q3 4. q7,
      1 - . 0
      \break

      6 ^"低八度" 1' 1' 0
      7 q6 q7 1' ^"I" 0
      q6 q7 q1' q6 q6 q5 q3 q1
      2 - . 0
      \break

      5 q3 q5 1'. q7
      6 1' 5 -
      5 q2 q3 4. q7,
      1 - . 0

.. versionadded:: 2.3

   and require `jianpu-ly`__ >=v1.856

   __ https://pypi.org/project/jianpu-ly/


Multiple MIDI Outputs
=====================

.. example:: _

   .. lily::

      \version "2.22.0"

      melody = \relative {
        \key c \major
        \time 4/4
        c'4 c g' g a a g2
        f4 f e e d d c2
      }

      harmony = \chordmode {
        c1: f2: c:
        f2: c: g2: c:
      }

      \book {
        \header {
          title = "Twinkle Twinkle Little Star"
          piece = \markup { \vspace #1 }
        }
        \score {
          <<
            \new ChordNames { \harmony }
            \new Staff { \melody }
            \addlyrics {
              Twin -- kle, twin -- kle, lit -- tle star,
              how I won -- der what you are! 
            }
          >>
          \layout {}
          \midi {}
        }
      }

      \book {
        \header { title = "Twinkle Twinkle Little Star (Melody)" }
        \score {
          \new Staff { \melody }
          \midi {}
        }
      }

      \book {
        \header { title = "Twinkle Twinkle Little Star (Harmony)" }
        \score {
          \new ChordNames { \harmony }
          \midi {}
        }
      }

.. versionadded:: 2.4
