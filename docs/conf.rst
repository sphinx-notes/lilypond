=============
Configuration
=============

.. hint:: In most cases, the extension should work without any configuration.

.. confval:: lilypond_lilypond_args:
   :type: list[str]
   :default: ['lilypond']
   :versionadded: 1.4

   Argument list for running `LilyPond`_. The first one is path to LilyPond binary.

.. confval:: lilypond_timidity_args
   :type: list[str]
   :default: ['timidity']

   Argument list for running `Timidity++`_. The first one is path to Timidity++ binary.

.. confval:: lilypond_ffmpeg_args
   :type: list[str]
   :default: ['ffmpeg']

   Argument list for running FFmpeg_. The first one is path to FFmpeg binary.

.. confval:: lilypond_score_format
   :Type: str
   :default: 'png'
   :choice: 'png' 'svg' 'pdf' 'eps'

   Format of outputed scores

.. confval:: lilypond_audio_format
   :type: str
   :default: 'wav'
   :choice: 'wav' 'ogg' 'mp3'
   :versionchanged:
      1.4
      Add support for 'mp3' audio format

   Format of outputed audio, available values:

.. confval:: lilypond_audio_volume
   :type: int
   :default: none
   :versionadded: 1.2

   Volume of outputed audio, will be converted to value of `Timidity++`_ argument ``--volume``.

.. confval:: lilypond_png_resolution
   :type: int
   :default: 300
   :versionadded: 1.1

   Resolution in DPI of score in PNG format, will be converted to value of LilyPond_ argument ``-dresolution``.

.. confval:: lilypond_inline_score_size
   :type: str
   :default: '2.5em'
   :versionadded: 1.1

   Line height of :ref:`inline socre <lily-role>`, will be converted to value of `CSS height`_.

.. confval:: lilypond_include_paths
   :type: list[str]
   :default: []
   :versionadded: 2.4

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

.. _LilyPond: https://lilypond.org/
.. _FFmpeg: https://ffmpeg.org/
.. _Timidity++: http://timidity.sourceforge.net/
.. _CSS height: https://developer.mozilla.org/en-US/docs/Web/CSS/height
.. _Including LilyPond files: https://lilypond.org/doc/Documentation/notation/including-lilypond-files
