=============
Configuration
=============

.. hint:: Normally, extensions should work without any configuration

:lilypond_lilypond_args: (Type: ``list[str]``, Default: ``['lilypond']``)
   Argument list for running `LilyPond`_. The first one is path to LilyPond binary.
:lilypond_timidity_args: (Type: ``list[str]``, Default: ``['timidity']``)
   Argument list for running `Timidity++`_. The first one is path to Timidity++ binary.
:lilypond_ffmpeg_args: (Type: ``list[str]``, Default: ``['ffmpeg']``)
   Argument list for running FFmpeg_. The first one is path to FFmpeg binary.

   .. versionadded:: 1.4

:lilypond_score_format: (Type: ``str``, Default: ``'png'``)
   Format of outputed scores, available values: ``['png', 'svg', 'pdf', 'eps']``.
:lilypond_audio_format: (Type: ``str``, Default: ``'wav'``)
   Format of outputed audio, available values: ``['wav', 'ogg', 'mp3']``.

   .. versionchanged:: 1.4

      Add support for 'mp3' audio format

:lilypond_audio_volume: (Type: ``int``, Default: `None`)
   Volume of outputed audio, will be converted to value of `Timidity++`_ argument ``--volume``.

   .. versionadded:: 1.2

:lilypond_png_resolution: (Type: ``int``, Default: ``300``)
   Resolution in DPI of score in PNG format, will be converted to value of LilyPond_ argument ``-dresolution``.

   .. versionadded:: 1.1
    
:lilypond_inline_score_size: (Type: ``str``, Default: ``2.5em``)
   Line height of :ref:`inline socre <lily-role>`, will be converted to value of `CSS height`_.

   .. versionadded:: 1.1


.. _LilyPond: https://lilypond.org/
.. _FFmpeg: https://ffmpeg.org/
.. _Timidity++: http://timidity.sourceforge.net/
.. _CSS height: https://developer.mozilla.org/en-US/docs/Web/CSS/height
