.. sphinxnotes-lilypond documentation master file, created by
   sphinx-quickstart on Sat Nov 28 00:42:50 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=============================
Sphinx Extension for LilyPond
=============================

:version: |version|
:copyright: Copyright ©2020 by Shengyu Zhang.
:copyright: Copyright ©2009 by Wei-Wei Guo.
:license: BSD, see LICENSE for details.

.. include:: desc.rst

.. contents::
   :local:
   :backlinks: none

Installation
============

Install the follwing runtime dependencies before using the extension:

- `LilyPond`_
- `TiMidity++`_
- `ImageMagick`_

.. _Timidity++: http://timidity.sourceforge.net/
.. _ImageMagick: https://imagemagick.org/index.php

Download it from official Python Package Index:

.. code-block:: console

   $ pip install sphinxnotes-lilypond

Add extension to :file:`conf.py` in your sphinx project:

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

.. literalinclude:: ./lily-role-example.rst
    :language: rst

Will be rendered as:

    .. include:: ./lily-role-example.rst

.. note::

    Role ``lily`` produces a preview image of the music expression (using
    ``-dpreview=#t``). You can still write a long music expression as interpreted text,
    but only the beginning can be shown.

Directives
----------

.. _lily-directive:

The ``lily`` directive
~~~~~~~~~~~~~~~~~~~~~~

The ``lily`` directive is used to insert a complete LilyPond score as
block level element.

.. literalinclude:: ./lily-directive-example.rst
    :language: rst

Will be rendered as:

    .. include:: ./lily-directive-example.rst

The directive supports the following options:

:noheader: (flag)
    Whether to remove the header of score
:nofooter: (flag)
    Whether to remove the footer of score
:noedge: (flag)
    Whether to remove the blank edges of score
:audio: (falg)
    Whether to show a audio player for listen LilyPond-generated MIDI file
:transpose: (text)
    Transposing the pitches of score from one to another.
    Pitches are written in `LilyPond Notation`_ and separated in whitespace.
    For example: ``:transpose: c' d'``

.. _LilyPond Notation: http://lilypond.org/doc/v2.18/Documentation/notation/writing-pitches

The ``lilyinclude`` directives
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``lilyinclude`` directive is similar to :ref:`lily-directive`,
except the source of LilyPond are read from file but not contents of directive.

.. literalinclude:: ./lilyinclude-directive-example.rst
   :language: rst

Will be rendered as:

   .. include:: ./lilyinclude-directive-example.rst

Options of the directive are same to :ref:`lily-directive`.

.. seealso::

    You and download the example LilyPond documentation from here:
    :download:`witch-spring.ly`.

Configuration
=============

:lilypond_lilypond_args: (Type: ``list[str]``, Default: ``['lilypond']``)
   Argument list for running `LilyPond`_. The first one is path to LilyPond binary.
:lilypond_timidity_args: (Type: ``list[str]``, Default: ``['timidity']``)
   Argument list for running `Timidity++`_. The first one is path to Timidity++ binary.
:lilypond_magick_home: (Type: ``str``, Default: ``None``)
   Path to `ImageMagick`_ library.
:lilypond_builddir: (Type: ``str``, Default: ``None``)
   Build directory of the extension, use temporary directory when not specified

Examples
========

The LilyPond documentation used in example can be downloaded here:
:download:`/minuet-in-g.ly`.

Original paper size
-------------------

.. code-block:: rst

   .. lilyinclude:: minuet-in-g.ly


.. lilyinclude:: minuet-in-g.ly

Paper without Footer and Edge
-----------------------------

.. code-block:: rst

   .. lilyinclude:: minuet-in-g.ly
      :nofooter:
      :noedge:

.. lilyinclude:: minuet-in-g.ly
   :nofooter:
   :noedge:
 
Smallest Paper Size
-------------------

.. code-block:: rst

   .. lilyinclude:: minuet-in-g.ly
      :noheader:
      :nofooter:
      :noedge:

.. lilyinclude:: minuet-in-g.ly
   :noheader:
   :nofooter:
   :noedge:

Audio Preview
-------------

.. code-block:: rst

   .. lilyinclude:: minuet-in-g.ly
      :noheader:
      :nofooter:
      :noedge:
      :audio:

.. lilyinclude:: minuet-in-g.ly
   :noheader:
   :nofooter:
   :noedge:
   :audio:

Transposing
------------

.. code-block:: rst

   .. lilyinclude:: minuet-in-g.ly
      :noheader:
      :nofooter:
      :noedge:
      :audio:
      :transpose: g c

.. lilyinclude:: minuet-in-g.ly
   :noheader:
   :nofooter:
   :noedge:
   :audio:
   :transpose: g c

Chang Log
=========

2020-12-06 1.0a1
----------------

 .. sectionauthor:: Shengyu Zhang

The alpha version is out, enjoy~
