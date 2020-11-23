from __future__ import annotations
import subprocess

from ly import pitch
from ly import document
from ly import docinfo
from ly import music
from ly import lex
from ly.pitch import transpose
from ly.music import read
from ly.music import items

# from sphinxnotes.base import LilyPondExtensionError

class LilyPondDocumentError(Exception):
    pass

class LilyPondDocument(object):

    _document:document.Document = None
    _lilypond_path:str = ''
    _score_format:str = 'png'
    _audio_format:str = ''

    def __init__(self, doc:str, lilypond_path:str='lilypond'):
        self._document = document.Document(doc)
        self._lilypond_path = lilypond_path

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

    def trim(self, trim_border=True, trim_header=True, trim_footer=True):
        # Find \paper block, if not found, we create one
        if True:
            doc = music.document(self._document)
            if not doc.find_child(items.Paper):
                self._document[0:0] = '''\paper {\n}'''

        # If more than one ``\paper`` is entered at the top level
        # the definitions are combined, but in conflicting situations
        # the later definitions take precedence [#]_
        #
        # .. [#] https://lilypond.org/doc/v2.20/Documentation/notation/file-structure
        #
        # So we only edit the last paper block

        if trim_border:
            doc = music.document(self._document)
            paper = list(doc.find_children(items.Paper))[-1]
            self._set_value(paper, 'indent', '0\mm')

        if trim_header:
            doc = music.document(self._document)
            paper = list(doc.find_children(items.Paper))[-1]
            self._set_value(paper, 'oddHeaderMarkup', '##f')
            self._set_value(paper, 'evenHeaderMarkup', '##f')
            self._set_value(paper, 'bookTitleMarkup', '##f')
            self._set_value(paper, 'scoreTitleMarkup', '##f')

        if trim_footer:
            doc = music.document(self._document)
            paper = list(doc.find_children(items.Paper))[-1]
            self._set_value(paper, 'oddFooterMarkup', '##f')
            self._set_value(paper, 'evenFooterMarkup', '##f')

    def set_audio_format(self, fmt:str):
        self._audio_format = fmt

    def set_score_format(self, fmt:str):
        self._score_format = fmt

    def output(self, base_name:str):
        args = [self._lilypond_path]
        if self._score_format in ['png', 'pdf', 'ps', 'eps']:
            args += ['--formats', self._score_format]
        elif self._score_format == 'svg':
            args += ['-dbackend=svg']
        else:
            raise LilyPondDocumentError('Unknown output format: {}' %
                    self._score_format)

        args += ['-dno-gs-load-fonts']
        args += ['-o', base_name]
        args += ['-'] # Read lilypond source from STDIN

        encoding = self._document.encoding or 'utf-8'
        try:
            p = subprocess.run(args,
                    input=self._document.plaintext(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding=encoding)
        except OSError:
            raise
        if p.returncode != 0:
            raise LilyPondDocumentError(
                    'LilyPond exited with error:\n[stderr]\n%s\n[stdout]\n%s' %
                    (p.stderr, p.stdout))

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

            
if __name__ == '__main__':
    doc = LilyPondDocument(r'''
\version "2.20.0"
\header {
  title = "《魔女之泉 1》开场音乐"
  composer = "Kiwi Walks"
  arranger = "SilverRainZ"
}

symbols =  {
  \time 4/4
  \tempo  "Allegretto" 4 = 110

  % 1
  c'4 c' c' c'8 b8
  c'4 g' c' c'8 b8
  c'4 g' (c'') c''8 b'8
  c''2 r2

  %14
  e'4 g c'2
  a8 c'8 c'8 d'8 c'2

  e'4 g' c'2
  c'4 d'8 e'8 c'4 g

  e'4 g c'2
  a8 c'8 c'8 d'8 e'4 c'

  g4 f e f8 g8

  \bar "|."
}

\score {
  <<
    \new Staff {
      \clef "G_8"
      \symbols
    }
    \new TabStaff {
      \tabFullNotation
      \symbols
    }
  >>

  \midi { }
  \layout { }
}''')
    print(doc._document.plaintext())
    # doc.trim()
    doc.output('test')
