.. sphinxnotes-lilypond documentation master file, created by
   sphinx-quickstart on Sat Nov 28 00:42:50 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=============================
Sphinx Extension for LilyPond
=============================

.. image:: https://img.shields.io/github/stars/sphinx-notes/lilypond.svg?style=social&label=Star&maxAge=2592000
   :target: https://github.com/sphinx-notes/lilypond

:version: |version|
:copyright: Copyright ©2020-2021 by Shengyu Zhang.
:copyright: Copyright ©2009 by Wei-Wei Guo.
:license: BSD, see LICENSE for details.

The extension is originated from `sphinx-contrib/lilypond`_ , allows `LilyPond`_
music notes to be included in Sphinx-generated documents inline and outline.
Compared to its predecessor, the extension has many new features such as
scale transposing, audio output, layout controlling, and so on.

.. _sphinx-contrib/lilypond: https://github.com/sphinx-contrib/lilypond
.. _LilyPond: https://lilypond.org/

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

.. _lily-role:

The ``lily`` role
~~~~~~~~~~~~~~~~~

You can use ``lily`` role to insert short `LilyPond Music Expression`_ as inline
element.

.. _LilyPond Music Expression: http://lilypond.org/doc/v2.19/Documentation/learning/music-expressions-explained

For example:

.. literalinclude:: ./lily-role-example.txt
    :language: rst

Will be rendered as:

    .. include:: ./lily-role-example.txt

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

.. literalinclude:: ./lily-directive-example.txt
    :language: rst

Will be rendered as:

    .. include:: ./lily-directive-example.txt

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

    .. _LilyPond Notation: http://lilypond.org/doc/v2.18/Documentation/notation/writing-pitches

:controls: (text, one of the ``top`` or ``bottom``)
    Specify the position of the control bar relative to the score.
    This implies ``audio``.

    .. versionadded:: 1.3

The ``lilyinclude`` directives
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``lilyinclude`` directive is similar to :ref:`lily-directive`,
except the source of LilyPond are read from file but not contents of directive.

.. literalinclude:: ./lilyinclude-directive-example.txt
   :language: rst

Will be rendered as:

   .. include:: ./lilyinclude-directive-example.txt

Options of the directive are same to :ref:`lily-directive`.

.. seealso::

    You and download the example LilyPond documentation from here:
    :download:`witch-spring.ly`.

Configuration
=============

.. hint:: Normally, extensions can work without any configuration

:lilypond_lilypond_args: (Type: ``list[str]``, Default: ``['lilypond']``)
   Argument list for running `LilyPond`_. The first one is path to LilyPond binary.
:lilypond_timidity_args: (Type: ``list[str]``, Default: ``['timidity']``)
   Argument list for running `Timidity++`_. The first one is path to Timidity++ binary.
:lilypond_magick_home: (Type: ``str``, Default: ``None``)
   Path to `ImageMagick`_ library.
:lilypond_score_format: (Type: ``str``, Default: ``'png'``)
   Format of outputed scores, available values: ``['png', 'svg', 'pdf', 'eps']``.
:lilypond_audio_format: (Type: ``str``, Default: ``'wav'``)
   Format of outputed audio, available values: ``['wav', 'ogg']``.
:lilypond_audio_volume: (Type: ``int``, Default: `None`)
   Volume of outputed audio, will be converted to value of `Timidity++`_ argument ``--volume``.

    .. versionadded:: 1.2

:lilypond_png_resolution: (Type: ``int``, Default: ``300``)
   Resolution in DPI of score in PNG format, will be converted to value of LilyPond_ argument ``-dresolution``.

    .. versionadded:: 1.1
    
:lilypond_inline_score_size: (Type: ``str``, Default: ``2.5em``)
   Line height of :ref:`inline socre <lily-role>`, will be converted to value of `CSS height`_.

    .. versionadded:: 1.1

.. _CSS height: https://developer.mozilla.org/en-US/docs/Web/CSS/height

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

Multiple Pages
--------------

.. code-block:: rst

   .. lilyinclude:: alice.ly
      :noedge:
      :audio:

.. lilyinclude:: alice.ly
   :noedge:
   :audio:

Loop
----

.. versionadded:: 1.2

.. code-block:: rst

   .. lilyinclude:: minuet-in-g.ly
      :noheader:
      :nofooter:
      :noedge:
      :loop:

.. lilyinclude:: minuet-in-g.ly
   :noheader:
   :nofooter:
   :noedge:
   :loop:

Control Bar at the Top
----------------------

.. versionadded:: 1.3

.. code-block:: rst

   .. lilyinclude:: minuet-in-g.ly
      :noheader:
      :nofooter:
      :noedge:
      :controls: top

.. lilyinclude:: minuet-in-g.ly
   :noheader:
   :nofooter:
   :noedge:
   :controls: top

Chang Log
=========

2021-11-07 1.3
--------------

- Add ``controls`` flag for specifing the position of the control bar

2021-09-17 1.2
--------------

- Simplify argument passing between lilypond binding and sphinx extension
- Add ``loop`` flag for directives
- Add confval ``lilypond_audio_volume``

2021-09-12 1.1
--------------

* Add confval ``lilypond_png_resolution`` for customizing score resolution in PNG format
* Add confval ``lilypond_inline_score_size`` for customizing height of :ref:`inline score <lily-role>`
* Stop using ``<figure>`` as container of block-level score, which is buggy on Safari

2021-06-26 1.0
--------------

* Rebuild env when configuration changed
* Fix wrong license value

2020-12-27 1.0a2
----------------

* Support multiple pages documents
* Imporve of lilypond outputs cache

2020-12-26 1.0a1
----------------

* Fix invalid insertion of ``\header``
* Set default audio format to wav

2020-12-06 1.0a0
----------------

The alpha version is out, enjoy~
