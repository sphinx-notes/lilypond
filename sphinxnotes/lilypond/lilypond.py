# -*- coding: utf-8 -*-
"""
    sphinxnotes.lilypond.binding
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Lilypond binding for Sphinx extension.

    :copyright: Copyright ©2020 by Shengyu Zhang.
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import Optional
import os
from os import path
import subprocess
from packaging import version
from dataclasses import dataclass

from ly import pitch
from ly import document
from ly import docinfo
from ly import music
from ly import pkginfo
from ly.pitch import transpose
from ly.music import items
from wand import image

# Golbal bining config
class Config(object):
    lilypond_args:List[str]
    timidity_args:List[str]
    magick_home:List[str]

    score_format:str
    png_resolution:int

    audio_format:str
    audio_volume:List[str]


class Error(Exception):
    # TODO
    pass


class Output(object):
    """
    Helper for collecting LilyPond outputed files outputed by :class:`Document`.
    """
    BASENAME:str = 'music'

    outdir:str = None

    source:str = None
    score:Optional[str] = None
    preview:Optional[str] = None
    paged_scores:list[str] = []
    midi:Optional[str] = None
    audio:Optional[str] = None

    def __init__(self, outdir:str):
        self.outdir = outdir

        prefix = path.join(outdir, self.BASENAME)

        srcfn = prefix + '.ly'
        if path.isfile(srcfn):
            self.source = srcfn

        pvfn = prefix + '.preview.' + Config.score_format
        if path.isfile(pvfn):
            self.preview = pvfn

        scorefn = prefix + '.' + Config.score_format
        if path.isfile(scorefn):
            self.score = scorefn

        # May multiple scores generated
        if Config.score_format in ['png', 'svg']:
            if Config.score_format == 'png':
                pattern = prefix + '-page%d.png'
            elif Config.score_format == 'svg':
                pattern = prefix + '-%d.svg'
            i = 1
            while path.isfile(pattern % i):
                # NOTE: Dont use ``+=`` or ``append``
                # See: https://github.com/satwikkansal/wtfpython#-class-attributes-and-instance-attributes
                self.paged_scores = self.paged_scores + [pattern % i]
                i = i + 1

        if not (self.preview or self.score or self.paged_scores):
            raise Error('No score generated, please check "*.%s" files under "%s"' %
                        (self.BASENAME, outdir))

        midifn = prefix + '.midi'
        if path.isfile(midifn):
            self.midi = midifn

        audiofn = prefix + '.' + Config.audio_format
        if path.isfile(audiofn):
            self.audio = audiofn

    def relocate(self, newdir:str):
        """
        Loocate files to a new directory.

        .. note:: This method does not actually move the files.
        """
        l = len(self.outdir)
        self.source = newdir + self.source[l:]
        if self.score:
            self.score = newdir + self.score[l:]
        if self.preview:
            self.preview = newdir + self.preview[l:]
        for i, p in enumerate(self.paged_scores):
            self.paged_scores[i] = newdir + p[l:]
        if self.midi:
            self.midi = newdir + self.midi[l:]
        if self.audio:
            self.audio = newdir + self.audio[l:]

class Document(object):
    _document:document.Document = None

    def __init__(self, src:str):
        self._document = document.Document(src)

    def plaintext(self):
        return self._document.plaintext()

    def transpose(self, from_pitch:str, to_pitch:str):
        fp = pitch.Pitch(
                *pitch.pitchReader("nederlands")(from_pitch[0]),
                octave = pitch.octaveToNum(from_pitch[1:]))
        tp = pitch.Pitch(
                *pitch.pitchReader("nederlands")(to_pitch[0]),
                octave = pitch.octaveToNum(to_pitch[1:]))
        transposer = transpose.Transposer(fp, tp)
        cursor = document.Cursor(self._document)
        try:
            if version.parse(pkginfo.version) > version.parse("0.9"):
                transpose.transpose(cursor, transposer,
                        relative_first_pitch_absolute = True) # only consider lilypond >= 2.18 for now
            else:
                transpose.transpose(cursor, transposer)
        except pitch.PitchNameNotAvailable:
            language = docinfo.DocInfo(cursor.document).language()
            raise Error(
                    'Pitch names not available in "%s", skipping file: %s' %
                    (language, cursor.document.filename))


    def strip_header_footer(self, strip_header=False, strip_footer=False):
        """Strip header and footer from outputed scores. """

        # Return when nothing todo
        if not strip_header and not strip_footer:
            return

        # Find \paper block, if not found, we create one
        if not music.document(self._document).find_child(items.Paper):
            self._document[0:0] = """\paper {\n}\n"""

        if strip_header:
            doc = music.document(self._document)
            for paper in doc.find_children(items.Paper):
                self._set_value(paper, 'oddHeaderMarkup', '##f')
                self._set_value(paper, 'evenHeaderMarkup', '##f')
                self._set_value(paper, 'bookTitleMarkup', '##f')
                self._set_value(paper, 'scoreTitleMarkup', '##f')

        if strip_footer:
            doc = music.document(self._document)
            for paper in doc.find_children(items.Paper):
                self._set_value(paper, 'oddFooterMarkup', '##f')
                self._set_value(paper, 'evenFooterMarkup', '##f')

            doc = music.document(self._document)
            no_header_found = True
            for header in doc.find_children(items.Header):
                self._set_value(header, 'tagline', '##f')
                no_header_found = False
            if no_header_found:
                self._document[0:0] = r'\header { tagline = ##f }'


    def enable_audio_output(self):
        """
        Enable audio output for this document.
        In other words, insert ``\midi{}`` to every ``\score{}`` block.
        If no ``\score{}`` found, find music list under root node, pack it
        in ``\socre{}``, then call this function again.
        """
        no_score_found = True
        doc = music.document(self._document)
        for score in doc.find_children(items.Score): # \score
            no_score_found = False
            if not score.find_child(items.Midi):
                self._insert_into(score, '\midi {}')
                self._insert_into(score, '\layout {}') # FIXME
        if no_score_found:
            if self._pack_music_list():
                self.enable_audio_output()


    def output(self,
            outdir:str,
            preview:bool,
            crop:bool) -> Output:
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

        if preview:
            args += ['-dpreview=#t']

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

        if crop:
            if out.score:
                self._crop(out.score)
            for p in out.paged_scores:
                self._crop(p)

        if preview and not out.preview:
            raise Error('No score preview file generated, please check "%s"' % outdir)

        return out


    def _replace_item(self, item:items.Item, new_item:str):
        """
        Replace the text at position of given item to new_item.
        Note that the position of other music items on same tree may be influenced
        after replacement.
        """
        with self._document as d:
            d[item.position:item.end_position()] = new_item


    def _insert_into(self, container:items.Container, item:str):
        """
        Insert the text into position of given container.
        Note that the position of other music items on same tree may be influenced
        after insertion.
        """
        with self._document as d:
            d[container.end_position()-1:container.end_position()-1] = '\n' + item + '\n'


    def _insert_before(self, container:items.Container, item:str):
        """
        Insert the text before position of given container.
        Note that the position of other music items on same tree may be influenced
        after insertion.
        """
        with self._document as d:
            d[container.position:container.position] = '\n' + item + '\n'


    def _insert_after(self, container:items.Container, item:str):
        """
        Insert the text after position of given container.
        Note that the position of other music items on same tree may be influenced
        after insertion.
        """
        with self._document as d:
            d[container.end_position():container.end_position()] = '\n' + item + '\n'


    def _set_value(self, container:items.Container, name:str, val:str):
        found = False
        children = list(container.find_children(items.Assignment))
        if children:
            # Reverse list to prevent replacement influences the position of token
            for a in reversed(children):
                if a.name() == name:
                    self._replace_item(a.value(), val)
                    found = True
        if not found:
            # Insert a assignment expression directly when nothing found
            self._insert_into(container, name + ' = ' + val)


    def _crop(self, scorefn:str):
        if Config.magick_home:
            old_magick_home = os.environ["MAGICK_HOME"]
            os.environ["DEBUSSY"] = Config.magick_home
        with image.Image(filename=scorefn) as i:
            i.trim()
            i.save(filename=scorefn)
        if Config.magick_home:
            if old_magick_home:
                os.environ["MAGICK_HOME"] = old_magick_home
            else:
                del os.environ["MAGICK_HOME"]


    def _midi_to_audio(self, midifn:str):
        try:
            timidity_args = Config.timidity_args.copy()
            if Config.audio_format == 'ogg':
                timidity_args += ['-Ov']
            elif Config.audio_format == 'wav':
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


    def _pack_music_list(self) -> bool:
        """
        Find music list under root node, pack it in ``\socre{}``.
        Return turn when at least one music list is packed.
        """
        packed = False
        doc = music.document(self._document)
        for mit in doc.find_children(items.MusicList):
            if mit.parent() == doc:
                self._insert_after(mit, r'}')
                self._insert_before(mit, r'\score {')
                packed = True
            elif isinstance(mit.parent(), (items.Relative, items.Absolute)) \
                    and mit.parent().parent() == doc:
                self._insert_after(mit.parent(), r'}')
                self._insert_before(mit.parent(), r'\score {')
                packed = True
        return packed


    def _merge_pages(self, scorefns:list[str]):
        # TODO
        pass
