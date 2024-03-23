.. This file is generated from sphinx-notes/cookiecutter.
   You need to consider modifying the TEMPLATE or modifying THIS FILE.

==========
Change Log
==========

.. Example:

   1.0.0
   =====

   .. version:: _
      :date: yyyy-mm-dd

      Change log here.

Version 2.x
-----------

.. version:: 2.1
   :date: 2024-03-23

   - Support :example:`Playable Inline Score` (:pull:`39`)
   - Update jianpu-ly submodule to v1.75
   - Document improvements

.. version:: 2.0.1
   :date: 2023-08-19

   - Compat with Sphinx 7.2's changes

.. version:: 2.0.0
   :date: 2023-08-18

   .. warning:: This release introduces some BREAKING changes.

   - **BREAKING** changes:

     - Drop ``:noheader``, ``:nofooter:`` options. User should modifying their Lilypond
       source to removing header and footer of scores, see `Custom titles headers and footers`__
       for more details (:issue:`35`)
     - Drop ``:noedge:`` option and introduce ``:nocrop:`` with opposite meaning compared to before.
       It is said that score is croppped (noedge) by default
       By the way, dependencies to Wand and ImageMagick are dropped (:issue:`31`)
     - Drop ``:audio:`` option and introduce ``:noaudio:`` with opposite meaning compared to before.
       Audio will be auto-generated when any `MIDI output`__ avaliable, and user set `:noaudio:`
       only when they don't need this behavior (:pull:`36`)

   - Enhanced Jianpu support (:issue:`30`)

     - Don't panic when Jianpu parsing failed
     - Can display multiple Jianpu scores, see also `jianpu-ly#35`__
     - Audio works fine now

   - Score image generataion is reproducible now (:issue:`10`)

   __ https://lilypond.org/doc/Documentation/notation/creating-titles-headers-and-footers
   __ https://lilypond.org/doc/Documentation/notation/the-midi-block
   __ https://github.com/ssb22/jianpu-ly/issues/35

Version 1.x
-----------

.. version:: 1.6.1
   :date: 2023-06-09

   - Support including score from abs path (:pull:`25`)

.. version:: 1.6.0
   :date: 2022-10-08

   - Fix resolution of SVG output (:pull:`18`)
   - Add basic Jianpu (Numbered Musical Notation) support (:issue:`17`)
   - Don't panic when running unsupported builders (:issue:`20`)

.. version:: 1.5
   :date: 2022-03-13

   - Add LaTeX builder suppport (:issue:`11`)

.. version:: 1.4
   :date: 2021-12-19

   - Note ly files as dependencies, so Sphinx will rebuild document when ly file changes
   - Won't crash when score file does not exist
   - Left a "system message" paragraphs when score build failed
   - Add support for MP3 audio format, FFmpeg_ is required

   .. _FFmpeg: https://ffmpeg.org/

.. version:: 1.3
   :date: 2021-11-07

   - Add ``controls`` flag for specifing the position of the control bar

.. version:: 1.2
   :date: 2021-09-17

   - Simplify argument passing between lilypond binding and sphinx extension
   - Add ``loop`` flag for directives
   - Add confval :confval:`lilypond_audio_volume`

.. version:: 1.1
   :date: 2021-09-12

   - Add confval :confval:`lilypond_png_resolution` for customizing score resolution in PNG format
   - Add confval :confval:`lilypond_inline_score_size` for customizing height of :ref:`inline score <lily-role>`
   - Stop using ``<figure>`` as container of block-level score, which is buggy on Safari

.. version:: 1.0
   :date: 2021-06-26

   - Rebuild env when configuration changed
   - Fix wrong license value

Pre-release
-----------

.. version:: 1.0a2
   :date: 2020-12-27

   - Support multiple pages documents
   - Imporve of lilypond outputs cache

.. version:: 1.0a1
   :date: 2020-12-26

   - Fix invalid insertion of ``\header``
   - Set default audio format to wav

.. version:: 1.0a0
   :date: 2020-12-06

   The alpha version is out, enjoy~
