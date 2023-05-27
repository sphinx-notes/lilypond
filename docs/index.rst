.. This file is generated from sphinx-notes/template.
   You need to consider modifying the TEMPLATE or modifying THIS FILE.

.. include:: ../README.rst

Introduction
============

.. ADDITIONAL CONTENT START

The extension is originated from `sphinx-contrib/lilypond`_ , allows `LilyPond`_
music notes :lily:`\relative { c' }` to be included in Sphinx-generated documents.
Compared to its predecessor, the extension has many new features such as:

- Scale :ref:`example-transposing`
- :ref:`example-audio-preview`
- Layout controlling
- LaTeX support (Since :version:`1.5`)
- And so on…

.. _sphinx-contrib/lilypond: https://github.com/sphinx-contrib/lilypond
.. _LilyPond: https://lilypond.org/

.. ADDITIONAL CONTENT END

Getting Started
===============

.. note::

   We assume you already have a Sphinx documentation,
   if not, see `Getting Started with Sphinx`_.

First, downloading extension from PyPI:

.. code-block:: console

   $ pip install sphinxnotes-lilypond

Then, add the extension name to ``extensions`` configuration item in your conf.py_:

.. code-block:: python

   extensions = [
             # …
             'sphinxnotes.lilypond',
             # …
             ]

.. _Getting Started with Sphinx: https://www.sphinx-doc.org/en/master/usage/quickstart.html
.. _conf.py: https://www.sphinx-doc.org/en/master/usage/configuration.html

.. ADDITIONAL CONTENT START

Install the follwing runtime dependencies before using the extension:

- `LilyPond`_
- `TiMidity++`_
- `FFmpeg`_
- `ImageMagick`_

.. note::
   
   A basic understanding of Lilypond notation is required, or you can refer to
   `LilyPond Learning Manual`_.

.. _FFmpeg: https://ffmpeg.org/
.. _Timidity++: http://timidity.sourceforge.net/
.. _ImageMagick: https://imagemagick.org/index.php
.. _LilyPond Learning Manual: https://lilypond.org/doc/Documentation/learning/index

We provide :ref:`roles` for embedding score fragment and :ref:`directives` for
embedding a whole socre:

.. grid:: 2

   .. grid-item-card:: Role

      .. literalinclude:: /_scores/lily-role.txt
          :language: rst

   .. grid-item-card:: Result

       .. include:: /_scores/lily-role.txt

.. grid:: 2

   .. grid-item-card:: Directive

      .. literalinclude:: /_scores/lily-directive-c-major-scale.txt
          :language: rst

   .. grid-item-card:: Result

       .. include:: /_scores/lily-directive-c-major-scale.txt

See :doc:`usage` for more details.

.. ADDITIONAL CONTENT END

Contents
========

.. toctree::
   :caption: Contents

   usage
   examples
   conf
   changelog

The Sphinx Notes Project
========================

This project is a developed by `Shengyu Zhang`__,
as part of **The Sphinx Notes Project**.

.. toctree::
   :caption: The Sphinx Notes Project

   Home <https://sphinx.silverrainz.me/>
   Blog <https://silverrainz.me/blog/category/sphinx.html>
   PyPI <https://pypi.org/search/?q=sphinxnotes>

__ https://github.com/SilverRainZ
