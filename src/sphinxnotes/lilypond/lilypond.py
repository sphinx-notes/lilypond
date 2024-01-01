# -*- coding: utf-8 -*-
"""
    sphinxnotes.lilypond.binding
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Lilypond binding for Sphinx extension.

    :copyright: Copyright ©2020 by Shengyu Zhang.
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
import os
from os import path
import subprocess
from packaging import version
import itertools

from ly import pitch
from ly import document
from ly import docinfo
from ly import pkginfo
from ly.pitch import transpose

# Golbal bining config
class Config(object):
    lilypond_args:list[str]
    timidity_args:list[str]
    ffmpeg_args:list[str]

    score_format:str
    png_resolution:int

    audio_format:str
    audio_volume:list[str]


class Error(Exception):
    # TODO
    pass


class Output(object):
    """
    Helper for collecting LilyPond outputed files outputed by :class:`Document`.
    """
    BASENAME:str = 'music'

    outdir:str

    source:str
    score: str|None
    paged_scores:list[str]
    cropped_score:str|None
    midi:str|None
    audio:str|None

    def __init__(self, outdir:str):
        self.outdir = outdir

        prefix = path.join(outdir, self.BASENAME)

        srcfn = prefix + '.ly'
        if not path.isfile(srcfn):
            raise Error('Lilypond source is not a file: %s' % srcfn)
        self.source = srcfn

        scorefn = prefix + '.' + Config.score_format
        self.score = scorefn if path.isfile(scorefn) else None

        croppedfn = prefix + '.cropped.' + Config.score_format
        self.cropped_score = croppedfn if path.isfile(croppedfn) else None

        # May multiple scores generated
        self.paged_scores = []
        if Config.score_format in ['png', 'svg']:
            if Config.score_format == 'png':
                pattern = prefix + '-page%d.png'
            elif Config.score_format == 'svg':
                pattern = prefix + '-%d.svg'
            else:
                raise Error('Unknown score format: %s' % Config.score_format )
            for i in itertools.count(start=1):
                if not path.isfile(pattern % i):
                    break
                self.paged_scores.append(pattern % i)

        if not any([self.score,
                    self.cropped_score,
                    self.paged_scores]):
            raise Error('No score generated, please check "*.%s" files under "%s"' %
                        (self.BASENAME, outdir))

        midifn = prefix + '.midi'
        self.midi = midifn if path.isfile(midifn) else None

        audiofn = prefix + '.' + Config.audio_format
        self.audio = audiofn if path.isfile(audiofn) else None

    def relocate(self, newdir:str):
        """
        Loocate files to a new directory.

        .. note:: This method does not actually move the files.
        """
        l = len(self.outdir)
        self.source = newdir + self.source[l:]
        if self.score:
            self.score = newdir + self.score[l:]
        if self.cropped_score:
            self.cropped_score = newdir + self.cropped_score[l:]
        for i, p in enumerate(self.paged_scores):
            self.paged_scores[i] = newdir + p[l:]
        if self.midi:
            self.midi = newdir + self.midi[l:]
        if self.audio:
            self.audio = newdir + self.audio[l:]


class Document(object):
    _document:document.Document

    def __init__(self, src:str):
        self._document = document.Document(src)

    def plaintext(self):
        return self._document.plaintext()

    def transpose(self, from_pitch:str, to_pitch:str):
        fp = pitch.Pitch(
            *pitch.pitchReader("nederlands")(from_pitch[0]), # type: ignore
            octave = pitch.octaveToNum(from_pitch[1:]))
        tp = pitch.Pitch(
            *pitch.pitchReader("nederlands")(to_pitch[0]), # type: ignore
            octave = pitch.octaveToNum(to_pitch[1:]))
        transposer = transpose.Transposer(fp, tp)
        cursor = document.Cursor(self._document)
        try:
            if version.parse(pkginfo.version) > version.parse("0.9"):
                # Only consider lilypond >= 2.18 for now.
                transpose.transpose(cursor, transposer, relative_first_pitch_absolute=True) # type: ignore
            else:
                transpose.transpose(cursor, transposer)
        except pitch.PitchNameNotAvailable:
            language = docinfo.DocInfo(cursor.document).language()
            raise Error(
                    'Pitch names not available in "%s", skipping file: %s' %
                    (language, cursor.document.filename))


    def output(self, outdir:str, crop:bool) -> Output:
        """Output scores and related files from LilyPond Document. """
        args = Config.lilypond_args.copy()
        args += ['-o', outdir]
        if Config.score_format in ['png', 'pdf', 'ps', 'eps']:
            args += ['--formats', Config.score_format]
            if Config.score_format == 'png':
                args += ['-dresolution=%d' % Config.png_resolution]
        elif Config.score_format == 'svg':
            args += ['-dbackend=svg']
        else:
            raise Error('Unknown score format: %s' % Config.score_format )

        if crop:
            args += ['-dcrop=#t']

        prefix = path.join(outdir, Output.BASENAME)
        srcfn = prefix + '.ly'
        with open(srcfn, 'w') as f:
            f.write(self.plaintext())
        args += [srcfn]

        try:
            p = subprocess.run(args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding=self._document.encoding or 'utf-8')
        except OSError as e:
            raise Error('LilyPond cannot be run') from e
        if p.returncode != 0:
            raise Error('LilyPond exited with error:\n[stderr]\n%s\n[stdout]\n%s' %
                    (p.stderr, p.stdout))

        # Generate audio
        midifn = prefix + '.midi'
        if path.isfile(midifn):
            self._midi_to_audio(midifn)

        out = Output(outdir)

        return out


    def _midi_to_audio(self, midifn:str):
        try:
            timidity_args = Config.timidity_args.copy()
            if Config.audio_format == 'ogg':
                timidity_args += ['-Ov']
            elif Config.audio_format in ['wav', 'mp3']:
                timidity_args += ['-Ow']
            else:
                raise Error('Unsupported audio format "%s"' % Config.audio_format)
            if Config.audio_volume:
                timidity_args += ['--volume=%d' % Config.audio_volume]
            timidity_args += [midifn]
            p = subprocess.run(timidity_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
        except OSError as e:
            raise Error('TiMidity++ cannot be run') from e
        except Exception as e:
            raise e
        if p.returncode != 0:
            raise Error(
                    'TiMidity++ exited with error:\n[stderr]\n%s\n[stdout]\n%s' %
                    (p.stderr, p.stdout))

        # Convert wav to mp3
        if Config.audio_format == 'mp3':
            ffmpeg_args = Config.ffmpeg_args.copy()
            wavfn = midifn[:-len('midi')] + 'wav'
            mp3fn = midifn[:-len('midi')] + 'mp3'
            ffmpeg_args += ['-i', wavfn, mp3fn]
            try:
                p = subprocess.run(ffmpeg_args,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
            except OSError as e:
                raise Error('FFmpeg cannot be run') from e
            except Exception as e:
                raise e
            finally:
                # Remove unused wav file
                os.remove(wavfn)
            if p.returncode != 0:
                raise Error(
                        'FFmpeg exited with error:\n[stderr]\n%s\n[stdout]\n%s' %
                        (p.stderr, p.stdout))
