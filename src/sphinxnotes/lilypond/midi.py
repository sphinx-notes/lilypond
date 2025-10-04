"""
sphinxnotes.lilypond.midi
~~~~~~~~~~~~~~~~~~~~~~~~~

MIDI related code.

:copyright: Copyright ©2025 by Shengyu Zhang.
:license: BSD, see LICENSE for details.
"""

import os
import subprocess

from mido import MidiFile

from sphinx.util import logging

logger = logging.getLogger(__name__)


class Error(Exception):
    pass


def to_audio(
    timidity_args: list[str],
    ffmpeg_args: list[str],
    audio_format: str,
    audio_volume: list[str],
    fn: str,
):
    try:
        timidity_args = timidity_args.copy()
        if audio_format == 'ogg':
            timidity_args += ['-Ov']
        elif audio_format in ['wav', 'mp3']:
            timidity_args += ['-Ow']
        else:
            raise Error('Unsupported audio format "%s"' % audio_format)
        if audio_volume:
            timidity_args += ['--volume=%d' % audio_volume]
        timidity_args += [fn]
        p = subprocess.run(
            timidity_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except OSError as e:
        raise Error('TiMidity++ cannot be run') from e
    except Exception as e:
        raise e
    if p.returncode != 0:
        raise Error(
            'TiMidity++ exited with error:\n[stderr]\n%s\n[stdout]\n%s'
            % (p.stderr, p.stdout)
        )

    # Convert wav to mp3
    if audio_format == 'mp3':
        ffmpeg_args = ffmpeg_args.copy()
        wavfn = fn[: -len('midi')] + 'wav'
        mp3fn = fn[: -len('midi')] + 'mp3'
        ffmpeg_args += ['-i', wavfn, mp3fn]
        try:
            p = subprocess.run(
                ffmpeg_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except OSError as e:
            raise Error('FFmpeg cannot be run') from e
        except Exception as e:
            raise e
        finally:
            # Remove unused wav file
            os.remove(wavfn)
        if p.returncode != 0:
            raise Error(
                'FFmpeg exited with error:\n[stderr]\n%s\n[stdout]\n%s'
                % (p.stderr, p.stdout)
            )


def get_track_name(fn: str) -> str | None:
    try:
        midi = MidiFile(fn)
    except Exception as e:
        logger.warning('failed to get title of MIDI file %s: %s', fn, e)
        return None
    for track in midi.tracks:
        for msg in track:
            if msg.type != 'track_name':
                continue
            # FIXME: It seems that in LilyPond 2.23+, the encoding of MIDI title
            # is UTF-8 rather that UTF-16. But we still found that 2.24.4
            # produces UTF-16 output.
            #
            # See also: https://gitlab.com/lilypond/lilypond/-/issues/6389
            return msg.name.encode('latin-1').decode('utf-8')
    return None
