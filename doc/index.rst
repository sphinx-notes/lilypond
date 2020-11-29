.. sphinxnotes-lilypond documentation master file, created by
   sphinx-quickstart on Sat Nov 28 00:42:50 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=======================================
Sphinx Extension for LilyPond |version|
=======================================

This extension is a fork of `sphinx-contrib/lilypond`_ ,
allows `LilyPond`_ music notes to be included in Sphinx-generated documents
inline and outline, provides richer features such as SVG format,
scale transposing, audio output and so on.

.. _sphinx-contrib/lilypond: https://github.com/sphinx-contrib/lilypond
.. _LilyPond: https://lilypond.org/

Installation
============

.. code-block:: console

   $ pip install sphinxnotes-lilypond

Add extension to :file:`conf.py` in your sphinx project.

.. code-block:: python

    extensions = [
              # …
              'sphinxnotes.lilypond',
              # …
              ]

Functionalities
===============

Roles
-----

The ``lily`` role
~~~~~~~~~~~~~~~~~

You can use ``lily`` role to insert short `LilyPond Music Expression`_ as inline
element.

.. _LilyPond Music Expression: http://lilypond.org/doc/v2.19/Documentation/learning/music-expressions-explained

For example:

.. code-block:: rst

    :lily:`\relative { c' }` is the first note of the C major scale.

Will be rendered as:

    :lily:`\relative { c' }` is the first note of the C major scale.

.. note::

    Role ``lily`` produces a preview image of the music expression.
    You can still write a long music expression as interpreted text,
    but only the beginning can be shown.

Directives
----------

.. _lily-directive:

The ``lily`` directive
~~~~~~~~~~~~~~~~~~~~~~

The ``lily`` directive is used to insert a complete lilypond document source.

.. code-block:: rst

   .. lily::
      :crop:

      \version "2.20.0"
      \header {
        title = "翼をください, Excerpts"
      }

      \score {
        <<
          \new Staff \relative c' {
              \time 4/4
              \tempo  "Allegretto" 4 = 110
              c4 d e e f e d
        }
        >>
      }

.. lily::
  :nofooter:
  :audio:

   \version "2.20.0"
   \header {
     title = "翼をください, Excerpts"
   }

   \score {
     <<
       \new Staff \relative c' {
           \time 4/4
           \tempo  "Allegretto" 4 = 110
           c4 d e e f e d
     }
     >>
   }

All available options:

:crop:
    directives.flag,
:audio:
    directives.unchanged, # control, autoplay,
:transpose:
    directives.unchanged,
:noheader:
    directives.flag,
:nofooter:
    directives.flag,


The ``lilyinclude`` directives
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. lilyinclude:: ./witch-spring.ly
   :nofooter:
   :crop:

Options of ``lilyinclude`` directive are same to :ref:`lily-directive`.

Configuration
=============

:lilypond_lilypond_args: (Default: ``['lilypond']``)
:lilypond_timidity_args: (Default: ``['timidity']``)
:lilypond_magick_home: (Default: ``None``)
:lilypond_builddir: (Default: ``None``)
