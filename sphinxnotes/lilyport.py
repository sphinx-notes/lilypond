# -*- coding: utf-8 -*-
"""
    Simple wrapper for LilyPond
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Allow Lilypond music notes to be transposed and converted to image, audio,
    and so on.

    :copyright: Copyright ©2020 by Shengyu Zhang.
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import Optional
import os
from os import path
import subprocess
import random
import string
from packaging import version

from ly import pitch
from ly import document
from ly import docinfo
from ly import music
from ly import pkginfo
from ly.pitch import transpose
from ly.music import items
from wand import image


def randstr() -> str:
    return 'music-' + ''.join(random.choice(string.ascii_lowercase) for i in range(5))


class Error(Exception):
    # TODO
    pass


class Output(object):
    '''A helper for collecting LilyPond outputed files.
    '''

    source:str
    score:Optional[str] = None
    preview:Optional[str] = None
    paged_scores:list[str] = []
    midi:Optional[str] = None
    audio:Optional[str] = None

    def __init__(self, outdir:str, basefn:str,
            score_format:str='png',
            audio_format:str='ogg'):
        prefix = path.join(outdir, basefn)

        srcfn = prefix + '.ly'
        if path.isfile(srcfn):
            self.source = srcfn

        pvfn = prefix + '.preview.' + score_format
        if path.isfile(pvfn):
            self.preview = pvfn

        scorefn = prefix + '.' + score_format
        if path.isfile(scorefn):
            self.score = scorefn

        # May multiple scores generated
        if score_format in ['png', 'svg']:
            if score_format == 'png':
                pattern = prefix + '-page%d.png'
            elif score_format == 'svg':
                pattern = prefix + '-%d.svg'
            i = 1
            while path.isfile(pattern % i):
                self.paged_scores.append(pattern % i)
                i = i + 1

        if not (self.preview or self.score or self.paged_scores):
            raise Error('No score generated, please check "*.%s" files under "%s"' %
                    (basefn, outdir))

        midifn = prefix + '.midi'
        if path.isfile(midifn):
            self.midi = midifn

        audiofn = prefix + '.' + audio_format
        if path.isfile(audiofn):
            self.audio = audiofn
            

class Document(object):

    _document:document.Document = None
    _lilypond_args:list[str] = []
    _timidity_args:list[str] = []
    _magick_home:Optional[str] = None

    def __init__(self, src:str,
            lilypond_args:list[str]=['lilypond'],
            timidity_args:list[str]=['timidity'],
            magick_home:Optional[str]=''):
        self._document = document.Document(src)
        self._lilypond_args = lilypond_args.copy()
        self._timidity_args = timidity_args.copy()
        self._magick_home = magick_home

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
                    'Pitch names not available in "{}", skipping file: {}' %
                    (language, cursor.document.filename))


    def strip_header_footer(self, strip_header=False, strip_footer=False):
        '''Strip header and footer from outputed scores
        '''

        # Return when nothing todo
        if not strip_header and not strip_footer:
            return

        # Find \paper block, if not found, we create one
        if not music.document(self._document).find_child(items.Paper):
            self._document[0:0] = '''\paper {\n}\n'''

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

            no_header_found = True
            for header in doc.find_children(items.Header):
                self._set_value(header, 'tagline', '##f')
                no_header_found = False
            self._document[0:0] = r'\header { tagline = ##f }'


    def enable_audio_output(self):
        '''Enable audio output for this document.
        In other words, insert ``\midi{}`` to every ``\score{}`` block.
        If no ``\score{}`` found, find music list under root node, pack it
        in ``\socre{}``, then call this function again.
        '''
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


    def output(self, outdir:str,
            basefn:str=randstr(),
            score_format:str='png',
            audio_format:str='ogg',
            preview:bool=False,
            crop:bool=True) -> Output:
        '''Output scores and related files from LilyPond Document
        '''
        args = self._lilypond_args.copy()
        args += ['-o', outdir]

        if score_format in ['png', 'pdf', 'ps', 'eps']:
            args += ['--formats', score_format]
        elif score_format == 'svg':
            args += ['-dbackend=svg']
        else:
            raise Error('Unknown score format: %s' % score_format )

        if preview:
            args += ['-dpreview=#t']

        srcfn = path.join(outdir, basefn) + '.ly'
        with open(srcfn, 'w') as f:
            f.write(self.plaintext())
        args += [srcfn]

        try:
            p = subprocess.run(args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding=self._document.encoding or 'utf-8')
        except OSError as e:
            raise Error('LilyPond can not be run') from e
        if p.returncode != 0:
            raise Error('LilyPond exited with error:\n[stderr]\n%s\n[stdout]\n%s' %
                    (p.stderr, p.stdout))

        # Generate audio
        midifn = path.join(outdir, basefn) + '.midi'
        if path.isfile(midifn):
            self._midi_to_audio(midifn, audio_format=audio_format)

        out = Output(outdir, basefn,
                score_format=score_format,
                audio_format=audio_format)

        if crop:
            if out.score:
                self._crop(out.score)
            for p in out.paged_scores:
                self._crop(p)

        if preview and not out.preview:
            raise Error('No score preview file generated, please check "%s"' % basefn)

        return out


    def _replace_item(self, item:items.Item, new_item:str):
        '''Replace the text at position of given item to new_item.
        Note that the position of other music items on same tree may be influenced
        after replacement.
        '''
        with self._document as d:
            d[item.position:item.end_position()] = new_item


    def _insert_into(self, container:items.Container, item:str):
        '''Insert the text into position of given container.
        Note that the position of other music items on same tree may be influenced
        after insertion.
        '''
        with self._document as d:
            d[container.end_position()-1:container.end_position()-1] = '\n' + item + '\n'


    def _insert_before(self, container:items.Container, item:str):
        '''Insert the text before position of given container.
        Note that the position of other music items on same tree may be influenced
        after insertion.
        '''
        with self._document as d:
            d[container.position:container.position] = '\n' + item + '\n'


    def _insert_after(self, container:items.Container, item:str):
        '''Insert the text after position of given container.
        Note that the position of other music items on same tree may be influenced
        after insertion.
        '''
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
        if self._magick_home:
            old_magick_home = os.environ["MAGICK_HOME"]
            os.environ["DEBUSSY"] = self._magick_home
        with image.Image(filename=scorefn) as i:
            i.trim()
            i.save(filename=scorefn)
        if self._magick_home:
            if old_magick_home:
                os.environ["MAGICK_HOME"] = old_magick_home
            else:
                del os.environ["MAGICK_HOME"]


    def _midi_to_audio(self, midifn:str, audio_format:str):
        if not audio_format in ['ogg']:
            raise Error('Unsupported audio format "%s"' % audio_format)

        try:
            p = subprocess.run(self._timidity_args + ['-Ov', midifn],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
        except OSError as e:
            raise Error('TiMidity++ can not be run') from e
        if p.returncode != 0:
            raise Error(
                    'TiMidity++ exited with error:\n[stderr]\n%s\n[stdout]\n%s' %
                    (p.stderr, p.stdout))


    def _pack_music_list(self) -> bool:
        '''Find music list under root node, pack it in ``\socre{}``.
        Return turn when at least one music list is packed.
        '''
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
