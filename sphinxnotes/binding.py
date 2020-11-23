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

# from sphinxnotes.base import LilyPondExtensionError

class LilyPondDocumentError(Exception):
    pass

class LilyPondOutput(object):

    _score_format:str = ''
    _audio_format:str = ''
    _tmpdir:str = ''
    _basename:str = 'music.ly'

    def __init__(self, score_format:str, audio_format:str):
        self._score_format = score_format
        self._audio_format = audio_format
        self._tempdir = tempfile.mkdtemp(prefix='sphinxnotes-lilypond')

    def base_path(self) -> str:
        return os.path.join(self._tempdir, self._basename)

    def score_preview(self) -> Optional[str]:
        f = os.path.join(self._tempdir, self._basename + '.preview.' + self._score_format)
        if os.path.isfile(f):
            return f

    def score(self) -> str:
        f = os.path.join(self._tempdir, self._basename + '.' + self._score_format)
        if os.path.isfile(f):
            return f

    def paged_scores(self) -> list[str]:
        raise NotImplementedError()

    def midi(self) -> list[str]:
        f = os.path.join(self._tempdir, self._basename + '.midi')
        if os.path.isfile(f):
            return f

    def audio(self) -> list[str]:
        f = os.path.join(self._tempdir, self._basename + '.' + self._audio_format)
        if os.path.isfile(f):
            return f

    def cleanup(self):
        try:
            shutil.rmtree(self._tempdir)
        except Exception:
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
            self._set_value(paper, 'indent', '0')
            self._set_value(paper, 'top-margin', '1')
            self._set_value(paper, 'bottom-margin', '1')
            self._set_value(paper, 'left-margin', '1')
            self._set_value(paper, 'right-margin', '1')

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

        out = LilyPondOutput(score_format=self._score_format, audio_format=self._audio_format)

        args += ['-dbackend=eps']
        args += ['-dpreview=#t'] # Enable preview
        args += ['-o', out.base_path()]
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
  title = "Alice"
  composer = "古川本舖"
  arranger = "Osamuraisan"
  copyright = "SilverRainZ"
}

prelude = \repeat unfold 2 {
    e,4 c g d
    f, c g d
    g, c g d
    g,8(a,8\6) c4 g d
}

interlude = \repeat unfold 2 {
  <e, g>4 c' d' g'
  <f, g>4 c' d' g'
  <g, g>4 c' d' g'
  <f, g>4 c' d' g'
}

pieceA = {
  <a, c'>4 e' <e, g'> g
}

pieceAi = {
  <f, c'>4 g' <c g'> g
}

pieceB = {
  <c a'>4 g8 c'8 <f, c'>4 d
}

pieceBi = {
  <d g'>4 (c'') <a c''> g
}

pieceBii = {
  <c c'>4 d <g, d'> d'
}

pieceBiii = {
  <c c'>4 d <g, d'> f'
}

pieceC = {
  <c a>4 c' <g, e'> d
}

pieceCi = {
  <d c'>4 g <g, e'> g
}

pieceCii = {
  <c c'>4 d' <a, e'> g8 e'8
}

pieceCiii = {
  <d e'>4 c' <a, c'> g8 e'8
}

pieceCiv = {
  <c c'>4 d' <a, e'> g
}

pieceD = {
  <g, d'>4 c' <a, c'> g
}

pieceDi = {
  <g, d'>4 f' <a, e'> d
}

pieceDii = {
  <g, d'>4 d8 c'8 <a, c'>4 d8 e'8
}

pieceDiii = {
  <g, d'>4 c' <f, c'> g
}

pieceDiv = {
  <g, d'>4 d8 c'8 <a, c'>2
}

symbols =  {
  \time 4/4
  \tempo  "Allegro" 4 = 150

  % 1
  \prelude

  %9
  \pieceA
  \pieceB
  \pieceC
  \pieceD

  %13
  \pieceA
  \pieceB
  \pieceC
  \pieceDi

  %17
  \pieceA
  \pieceB
  \pieceC
  \pieceD

  %21
  \pieceA
  \pieceBi
  \pieceCi
  \pieceD

  %25
  \pieceA
  \pieceB
  <c a>4 c' <g, e'> <d f'>
  \pieceD

  %29
  \pieceA
  \pieceB
  \pieceC
  \pieceDi

  %33
  \pieceA
  \pieceB
  \pieceC
  \pieceD

  %37
  \pieceA
  \pieceBi
  \pieceCi
  \pieceDii

  \bar "||"

  %41
  \pieceDiii

  %42
  \pieceAi
  \pieceBii
  \pieceCii
  \pieceDiii

  %46
  \pieceAi
  \pieceBiii
  \pieceCiii
  \pieceDiii

  %50
  \pieceAi
  \pieceBiii
  \pieceCiv

  %53
  \pieceA
  \pieceBi
  \pieceCi
  \pieceDii

  \bar "||"

  %57
  \pieceA
  \pieceB
  \pieceC
  \pieceD

  %61
  \pieceA
  \pieceB
  \pieceC
  \pieceDi

  %65
  \pieceA
  \pieceB
  \pieceC
  \pieceD

  %69
  \pieceA
  \pieceBi
  \pieceCi
  \pieceDiv

  \bar "||"

  %73
  \prelude

  %81
  \interlude

  \bar "||"

  %89
  r1
  r1

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
    doc.trim()
    print(doc._document.plaintext())
    doc.set_score_format('png')
    doc.output('test')
