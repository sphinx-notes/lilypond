from __future__ import annotations
from enum import Enum, auto
import subprocess

from ly import pitch
from ly import document 
from ly import docinfo 
from ly.pitch import transpose

# from sphinxnotes.base import LilyPondExtensionError

class LilyPondDocumentError(Exception):
    pass

class LilyPondDocument(object):

    document:document.Document = None
    lilypond_path:str = ''

    def __init__(self, doc:str, lilypond_path:str='lilypond'):
        self.document = document.Document(doc)
        self.lilypond_path = lilypond_path

    def transpose(self, from_pitch:str, to_pitch:str) -> LilyPondDocument:
        fp = pitch.Pitch(
                *pitch.pitchReader("nederlands")(from_pitch[0]),
                octave = pitch.octaveToNum(from_pitch[1:]))
        tp = pitch.Pitch(
                *pitch.pitchReader("nederlands")(to_pitch[0]),
                octave = pitch.octaveToNum(to_pitch[1:]))
        transposer = transpose.Transposer(fp, tp)
        cursor = document.Cursor(self.document)
        try:
            transpose.transpose(cursor, transposer,
                    relative_first_pitch_absolute = True) # Only consider LilyPond >= 2.18 for now
        except pitch.PitchNameNotAvailable:
            language = docinfo.DocInfo(cursor.document).language()
            raise LilyPondDocumentError(
                    'Pitch names not available in "{}", skipping file: {}' % 
                    (language, cursor.document.filename))

    def build_score(self, output_path:str, output_format:str='png'):
        args = [self.lilypond_path]
        if output_format in ['png', 'pdf', 'ps', 'eps']:
            args += ['--formats', output_format]
        elif output_format == 'svg':
            args += ['-dbackend=svg']
        else:
            raise LilyPondDocumentError('Unknown output format: {}' % output_format)

        args += ['-o', output_path]
        args += ['-'] # Read lilypond source from STDIN

        encoding = self.document.encoding or 'utf-8'
        try:
            p = subprocess.run(args,
                    input=self.document.plaintext(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding=encoding)
        except OSError:
            raise
        if p.returncode != 0:
            raise LilyPondDocumentError(
                    'LilyPond exited with error:\n[stderr]\n%s\n[stdout]\n%s' %
                    (p.stderr.decode('utf-8'), p.stdout.decode('utf-8')))

    def build_audio(output_path:str, output_format:str='ogg'):
        pass
            
# test
if __name__ == '__main__':
    doc = LilyPondDocument("{ c4 a d c }")
    doc.transpose("c", 'd')
    doc.build_score('./test.png', output_format='svg')
