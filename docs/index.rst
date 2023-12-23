.. This file is generated from sphinx-notes/cookiecutter.
   You need to consider modifying the TEMPLATE or modifying THIS FILE.

.. include:: ../README.rst

Introduction
============

.. ADDITIONAL CONTENT START

The extension is originated from `sphinx-contrib/lilypond`_ , allows `LilyPond`_
music notes :lily:`\relative { c' }` to be included in Sphinx-generated documents.
Compared to its predecessor, the extension has many new features such as:

- Play score audio (:doc:`examples`)
- LaTeX builder support (Since :version:`1.5`)
- Scale :example:`Transposing`
- :ref:`Jianpu <jianpu-directive>` (Numbered Musical Notation, 简谱) support (Since :version:`1.6.0`)
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

.. note::
   
   A basic understanding of Lilypond notation is required, or you can refer to
   `LilyPond Learning Manual`_.

.. _FFmpeg: https://ffmpeg.org/
.. _Timidity++: http://timidity.sourceforge.net/
.. _LilyPond Learning Manual: https://lilypond.org/doc/Documentation/learning/index

We provide :ref:`roles` for embedding score fragment and :ref:`directives` for
embedding a whole socre:

.. example::

   :lily:`\relative { c' }` is the first note of the C major scale.

.. example::

   .. lily::

      \version "2.20.0"
      \header {
        title = "C Major Scale"
      }

      \score {
        <<
          \new Staff {
              \time 4/4
              \tempo 4 = 70
              c' d' e' f' g' a' b' c''
        }
        >>

        \midi {}
        \layout {}
      }

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

+The project is developed by `Shengyu Zhang`__,
as part of **The Sphinx Notes Project**.

.. toctree::
   :caption: The Sphinx Notes Project

   Home <https://sphinx.silverrainz.me/>
   Blog <https://silverrainz.me/blog/category/sphinx.html>
   PyPI <https://pypi.org/search/?q=sphinxnotes>

__ https://github.com/SilverRainZ
