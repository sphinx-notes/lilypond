=============
Configuration
=============

.. hint:: In most cases, the extension should work without any configuration.

.. autoconfval:: lilypond_lilypond_args

   Argument list for running `LilyPond`_. The first one is path to LilyPond binary.
   
   .. versionadded:: 1.4

.. autoconfval:: lilypond_timidity_args

   Argument list for running `Timidity++`_. The first one is path to Timidity++ binary.

.. autoconfval:: lilypond_ffmpeg_args

   Argument list for running FFmpeg_. The first one is path to FFmpeg binary.

.. autoconfval:: lilypond_score_format

   :choice: 'png' 'svg' 'pdf' 'eps'

   Format of outputed scores.

.. autoconfval:: lilypond_audio_format

   Format of outputed audio, available values: ['wav', 'ogg', 'mp3']

   .. versionchanged:: 1.4

      Add support for 'mp3' audio format

.. autoconfval:: lilypond_audio_volume

   Volume of outputed audio, will be converted to value of `Timidity++`_ argument ``--volume``.

   .. versionadded:: 1.2

.. autoconfval:: lilypond_png_resolution

   Resolution in DPI of score in PNG format, will be converted to value of LilyPond_ argument ``-dresolution``.

   .. versionadded:: 1.1

.. autoconfval:: lilypond_inline_score_size

   Line height of :ref:`inline socre <lily-role>`, will be converted to value of `CSS height`_.

   .. versionadded:: 1.1

.. autoconfval:: lilypond_include_paths

   A list of paths relative to Sphinx source directory. It is used as additional
   search path for `Including LilyPond files`_, will be converted to
   value of LilyPond argument ``-I``/``--include``.

   For example, set ``lilypond_include_paths`` to ``/_scores``:

   .. grid:: 1 2 2 2

      .. grid-item::

         .. example:: Include another file

            .. lily::

               \version "2.24.0"

               \include "include.ly"

               \score {
                 \new Staff { \myMusic }
               }

      .. grid-item::

         |
         |
         |

         .. literalinclude:: /_scores/include.ly
            :caption: /_scores/include.ly

   .. versionadded:: 2.4

.. _LilyPond: https://lilypond.org/
.. _FFmpeg: https://ffmpeg.org/
.. _Timidity++: http://timidity.sourceforge.net/
.. _CSS height: https://developer.mozilla.org/en-US/docs/Web/CSS/height
.. _Including LilyPond files: https://lilypond.org/doc/Documentation/notation/including-lilypond-files
