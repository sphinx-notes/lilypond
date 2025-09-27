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
from pathlib import Path

from ly import pitch
from ly import document
from ly import docinfo
from ly import pkginfo
from ly.pitch import transpose

from . import midi


# Golbal bining config
class Config(object):
    lilypond_args: list[str]
    timidity_args: list[str]
    ffmpeg_args: list[str]

    score_format: str
    png_resolution: int
    include_paths: list[str]

    audio_format: str
    audio_volume: list[str]


class Error(Exception):
    pass


class Output(object):
    """
    Helper for collecting LilyPond outputed files outputed by :class:`Document`.
    """

    # TODO: Deal with custom output file name?
    # https://lilypond.org/doc/v2.24/Documentation/notation/output-file-names
    BASENAME: str = 'music'

    outdir: str

    source: str
    score: str | None
    paged_scores: list[str]
    cropped_score: str | None
    midis: list[str]
    tracks: list[str]  # MIDI track names, used as audio title
    audios: list[str]

    def __init__(self, outdir: str):
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
                raise Error('Unknown score format: %s' % Config.score_format)
            self.paged_scores += self._collect_by_index(pattern)

        if not any([self.score, self.cropped_score, self.paged_scores]):
            raise Error(
                'No score generated, please check "*.%s" files under "%s"'
                % (self.BASENAME, outdir)
            )

        self.midis = self._collect_by_ext(outdir, '.midi')
        self.audios = self._collect_by_ext(outdir, '.' + Config.audio_format)
        self.tracks = [midi.get_track_name(m) or Path(m).stem for m in self.midis]

    @staticmethod
    def _collect_by_index(pattern: str, start: int = 1) -> list[str]:
        files = []
        for i in itertools.count(start=start):
            if not path.isfile(pattern % i):
                break
            files.append(pattern % i)
        return files

    @staticmethod
    def _collect_by_ext(dir: str, ext: str) -> list[str]:
        files = []
        for f in os.listdir(dir):
            fullpath = path.join(dir, f)
            if fullpath.endswith(ext) and path.isfile(fullpath):
                files.append(fullpath)
        return sorted(files)

    def relocate(self, newdir: str):
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
        for i, p in enumerate(self.midis):
            self.midis[i] = newdir + p[l:]
        for i, p in enumerate(self.audios):
            self.audios[i] = newdir + p[l:]


class Document(object):
    _document: document.Document

    def __init__(self, src: str):
        self._document = document.Document(src)

    def plaintext(self):
        return self._document.plaintext()

    def transpose(self, from_pitch: str, to_pitch: str):
        fp = pitch.Pitch(
            *pitch.pitchReader('nederlands')(from_pitch[0]),  # type: ignore
            octave=pitch.octaveToNum(from_pitch[1:]),
        )
        tp = pitch.Pitch(
            *pitch.pitchReader('nederlands')(to_pitch[0]),  # type: ignore
            octave=pitch.octaveToNum(to_pitch[1:]),
        )
        transposer = transpose.Transposer(fp, tp)
        cursor = document.Cursor(self._document)
        try:
            if version.parse(pkginfo.version) > version.parse('0.9'):
                # Only consider lilypond >= 2.18 for now.
                transpose.transpose(
                    cursor, transposer, relative_first_pitch_absolute=True
                )  # type: ignore
            else:
                transpose.transpose(cursor, transposer)
        except pitch.PitchNameNotAvailable:
            language = docinfo.DocInfo(cursor.document).language()
            raise Error(
                'Pitch names not available in "%s", skipping file: %s'
                % (language, cursor.document.filename)
            )

    def output(self, outdir: str, crop: bool) -> Output:
        """Output scores and related files from LilyPond Document."""
        args = Config.lilypond_args.copy()
        args += ['-o', outdir]

        for i in Config.include_paths:
            args += ['--include', i]

        if Config.score_format in ['png', 'pdf', 'ps', 'eps']:
            args += ['--formats', Config.score_format]
            if Config.score_format == 'png':
                args += ['-dresolution=%d' % Config.png_resolution]
        elif Config.score_format == 'svg':
            args += ['-dbackend=svg']
        else:
            raise Error('Unknown score format: %s' % Config.score_format)

        if crop:
            args += ['-dcrop=#t']

        prefix = path.join(outdir, Output.BASENAME)
        srcfn = prefix + '.ly'
        with open(srcfn, 'w') as f:
            f.write(self.plaintext())
        args += [srcfn]

        try:
            p = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding=self._document.encoding or 'utf-8',
            )
        except OSError as e:
            raise Error('LilyPond cannot be run') from e
        if p.returncode != 0:
            raise Error(
                'LilyPond exited with error:\n[stderr]\n%s\n[stdout]\n%s'
                % (p.stderr, p.stdout)
            )

        # Generate audios.
        for fn in Output._collect_by_ext(outdir, '.midi'):
            self._midi_to_audio(fn)

        return Output(outdir)

    def _midi_to_audio(self, midifn: str):
        midi.to_audio(
            Config.timidity_args,
            Config.ffmpeg_args,
            Config.audio_format,
            Config.audio_volume,
            midifn,
        )
