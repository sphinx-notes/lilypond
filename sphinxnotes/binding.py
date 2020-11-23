from __future__ import annotations
from typing import Optional   
import os
import subprocess
import tempfile
import shutil

from ly import pitch
from ly import document
from ly import docinfo
from ly import music
from ly.pitch import transpose
from ly.music import items
from wand import image

class LilyPondDocumentError(Exception):
    pass

class LilyPondOutput(object):
    '''LilyPondOutput holds a set of files that output by LilyPond
    '''

    _score_format:str = ''
    _audio_format:str = ''
    _output_path:str = ''
    _basename:str = 'music'
    _is_tempdir:bool = True

    def __init__(self, score_format:str, audio_format:str, output_path:Optional[str]=None):
        self._score_format = score_format
        self._audio_format = audio_format
        if output_path:
            self._output_path = output_path    
        else:
            self._output_path = tempfile.mkdtemp(prefix='sphinxnotes-lilypond-')
            self._is_tempdir = True


    def base_path(self) -> str:
        return os.path.join(self._output_path, self._basename)


    def score_preview(self) -> Optional[str]:
        f = os.path.join(self._output_path, self._basename + '.preview.' + self._score_format)
        if os.path.isfile(f):
            return f


    def score(self) -> Optional[str]:
        f = os.path.join(self._output_path, self._basename + '.' + self._score_format)
        if os.path.isfile(f):
            return f


    def paged_scores(self) -> list[str]:
        ''' TODO '''
        return []


    def midi(self) -> Optional[str]:
        f = os.path.join(self._output_path, self._basename + '.midi')
        if os.path.isfile(f):
            return f


    def audio(self) -> Optional[str]:
        f = os.path.join(self._output_path, self._basename + '.' + self._audio_format)
        if os.path.isfile(f):
            return f


    def cleanup(self):
        if self._is_tempdir:
            return
        try:
            shutil.rmtree(self._output_path)
        except Exception:
            pass



class LilyPondDocument(object):

    _document:document.Document = None
    _lilypond_args:str = ''
    _score_format:str = 'png'
    _audio_format:str = 'ogg'

    def __init__(self, doc:str, lilypond_args:list[str]=['lilypond']):
        self._document = document.Document(doc)
        self._lilypond_args = lilypond_args.copy()

    def transpose(self, from_pitch:str, to_pitch:str) -> LilyPondDocument:
        fp = pitch.Pitch(
                *pitch.pitchReader("nederlands")(from_pitch[0]),
                octave = pitch.octaveToNum(from_pitch[1:]))
        tp = pitch.Pitch(
                *pitch.pitchReader("nederlands")(to_pitch[0]),
                octave = pitch.octaveToNum(to_pitch[1:]))
        transposer = transpose.Transposer(fp, tp)
        cursor = document.Cursor(self._document)
        try:
            transpose.transpose(cursor, transposer,
                    relative_first_pitch_absolute = True) # Only consider LilyPond >= 2.18 for now
        except pitch.PitchNameNotAvailable:
            language = docinfo.DocInfo(cursor.document).language()
            raise LilyPondDocumentError(
                    'Pitch names not available in "{}", skipping file: {}' %
                    (language, cursor.document.filename))

    def crop(self):
        doc = music.document(self._document)
        # If more than one ``\paper`` is entered at the top level
        # the definitions are combined, but in conflicting situations
        # the later definitions take precedence,
        # So we only edit the last paper block
        paper = list(doc.find_children(items.Paper))[-1]
        self._set_value(paper, 'indent', '0')
        self._set_value(paper, 'top-margin', '1')
        self._set_value(paper, 'bottom-margin', '1')
        self._set_value(paper, 'left-margin', '1')
        self._set_value(paper, 'right-margin', '1')

    def strip_header_footer(self, strip_header=True, strip_footer=True):
        '''Strip header and footer from outputed scores
        '''
        # Find \paper block, if not found, we create one
        if not music.document(self._document).find_child(items.Paper):
            self._document[0:0] = '''\paper {\n}'''

        if strip_header:
            doc = music.document(self._document)
            paper = list(doc.find_children(items.Paper))[-1]
            self._set_value(paper, 'oddHeaderMarkup', '##f')
            self._set_value(paper, 'evenHeaderMarkup', '##f')
            self._set_value(paper, 'bookTitleMarkup', '##f')
            self._set_value(paper, 'scoreTitleMarkup', '##f')

        if strip_footer:
            doc = music.document(self._document)
            paper = list(doc.find_children(items.Paper))[-1]
            self._set_value(paper, 'oddFooterMarkup', '##f')
            self._set_value(paper, 'evenFooterMarkup', '##f')


    def enable_audio_output(self):
        '''Enable audio output for this document.
        In other words, insert ``\midi{}`` to every ``\score{}`` block
        '''
        no_score_found = True
        doc = music.document(self._document)
        for score in doc.find_children(items.Score): # \score
            no_score_found = False
            if not score.find_child(items.Midi):
                self._insert_item(score, '\midi {}')
        if no_score_found:
            self._insert_item(doc, '\midi {}')


    def output(self,
            score_format:str='png',
            enable_preview:bool=False,
            crop_blank:bool=True,
            output_path:Optional[str]=None) -> LilyPondOutput:
        '''Output scores from LilyPond Document
        '''
        args = self._lilypond_args.copy()

        if score_format in ['png', 'pdf', 'ps', 'eps']:
            args += ['--formats', score_format]
        elif score_format == 'svg':
            args += ['-dbackend=svg']
        else:
            raise LilyPondDocumentError('Unknown score format: {}' % score_format )

        if enable_preview:
            args += ['-dpreview=#t']

        out = LilyPondOutput(
                score_format=score_format,
                audio_format='ogg',
                output_path=output_path) # Only ogg for now

        args += ['-o', out.base_path()]
        args += ['-'] # Read lilypond source from STDIN

        try:
            p = subprocess.run(args,
                    input=self._document.plaintext(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding=self._document.encoding or 'utf-8')
        except OSError:
            out.cleanup()
            raise
        if p.returncode != 0:
            out.cleanup()
            raise LilyPondDocumentError(
                    'LilyPond exited with error:\n[stderr]\n%s\n[stdout]\n%s' %
                    (p.stderr, p.stdout))

        if crop_blank:
            score_file = out.score()
            if score_file:
                self._crop_blank(score_file)
            for s in out.paged_scores():
                self._crop_blank(s)

        midi_file = out.midi()
        if midi_file:
            try:
                self._midi_to_audio(midi_file)
            except Exception as e:
                out.cleanup()
                raise e

        return out


    def _replace_item(self, item:items.Item, new_item:str):
        '''Replace the text at position of given item to new_item.
        Note that the position of other music items on same tree may be influenced
        after replacement.
        '''
        with self._document as d:
            d[item.position:item.end_position()] = new_item


    def _insert_item(self, container:items.Container, item:str):
        '''Insert the text into position of given container.
        Note that the position of other music items on same tree may be influenced
        after insertion.
        '''
        with self._document as d:
            d[container.end_position()-1:container.end_position()-1] = item + '\n'


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
            self._insert_item(container, name + '=' + val)


    def _crop_blank(self, score_file:str):
        with image.Image(filename=score_file) as i:
            i.trim()
            i.save(filename=score_file)


    def _midi_to_audio(self, midi_file:str):
        try:
            p = subprocess.run(['timidity', '-Ov', midi_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
        except OSError:
            raise
        if p.returncode != 0:
            raise LilyPondDocumentError(
                    'TiMidity++ exited with error:\n[stderr]\n%s\n[stdout]\n%s' %
                    (p.stderr, p.stdout))


    def _merge_pages(self, score_files:list[str]):
        ''' TODO '''
        pass
