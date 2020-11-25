# -*- coding: utf-8 -*-
"""
    Sphinx Extension for LilyPond
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Allow Lilypond music notes to be included in Sphinx-generated documents
    inline and outline.

    :copyright: Copyright ©2020 by Shengyu Zhang.
    :copyright: Copyright ©2009 by Wei-Wei Guo.
    :license: BSD, see LICENSE for details.

    The extension is modified from mathbase.py and pngmath.py by Sphinx team.
"""

import shutil
import posixpath
from os import path
from hashlib import sha1 as sha

from docutils import nodes
from docutils.utils import unescape
from docutils.parsers.rst import directives, Directive
from sphinx.util import ensuredir, relative_uri

from sphinxnotes import binding

_SCORE_CLASS = 'lilypond-score'
_AUDIO_CLASS = 'lilypond-audio'
_LILYPOND_DOC = 'lilypond-doc'

class lilypond_node(nodes.Inline, nodes.TextElement): pass

class lilypond_inline_node(nodes.Inline, nodes.TextElement): pass

class lilypond_outline_node(nodes.Part, nodes.Element): pass

def lilypond_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    node = lilypond_inline_node()
    node[_LILYPOND_DOC] = unescape(text, restore_backslashes=True)
    return [node], []

class LilyPondDirective(Directive):

    has_content = True
    required_arguments = 0
    optional_arguments = 5
    final_argument_whitespace = True
    option_spec = {
        'format': directives.unchanged,
        'crop': directives.flag,
        'no-audio': directives.flag,
        'no-header': directives.flag,
        'no-footer': directives.flag,
    }

    def run(self):
        node = lilypond_outline_node()
        node[_LILYPOND_DOC] = '\n'.join(self.content)
        node['docname'] = self.state.document.settings.env.docname
        return [node]

def copy_file(builder, node, srcfn:str, destdir: str) ->str:
    '''Copy file srcfn to builder's outdir, return a relative path to current
    document. If the file already exists in destdir, just return the relative path.
    '''
    _, ext = path.splitext(srcfn)
    shasum = sha(node[_LILYPOND_DOC].encode('utf-8')).hexdigest() + ext
    outfn = path.join(builder.outdir, destdir, 'lilypond', shasum)
    reluri = relative_uri(builder.get_target_uri(node['docname']), destdir)
    relfn = posixpath.join(reluri, 'lilypond', shasum)
    if path.isfile(outfn):
        return relfn
    ensuredir(path.dirname(outfn))
    shutil.copyfile(srcfn, outfn)
    return relfn


def copy_image_file(builder, node, imgfn:str) -> str:
    return copy_file(builder, node, imgfn, '_images')


def copy_audio_file(builder, node, audfn:str) -> str:
    return copy_file(builder, node, audfn, '_audio')


def html_visit_lilypond_inline_node(self, node):
    doc = binding.LilyPondDocument(node[_LILYPOND_DOC])
    try:
        out = doc.output(enable_preview=True)
    except binding.LilyPondDocumentError as e:
        sm = nodes.system_message(e, type='WARNING', level=2,
                                  backrefs=[], source=node[_LILYPOND_DOC])
        sm.walkabout(self)
        raise nodes.SkipNode

    imgfn = out.score_preview()
    if imgfn:
        imgfn = copy_image_file(self.builder, node, imgfn)
        self.body.append(
            '<img class="%s" src="%s" alt="%s" align="absbottom"/>' %
            (_SCORE_CLASS, imgfn, self.encode(node[_LILYPOND_DOC]).strip()))
    else:
        # Something failed -- use text-only as a bad substitute
        self.body.append('<span class="%s">%s</span>' %
                (_SCORE_CLASS, self.encode(node[_LILYPOND_DOC]).strip()))
    out.cleanup()
    raise nodes.SkipNode


def html_visit_lilypond_outline_node(self, node):
    doc = binding.LilyPondDocument(node[_LILYPOND_DOC])
    try:
        doc.enable_audio_output()
        doc.strip_header_footer()
        out = doc.output(crop_blank=True)
    except binding.LilyPondDocumentError as e:
        sm = nodes.system_message(e, type='WARNING', level=2,
                                  backrefs=[], source=node[_LILYPOND_DOC])
        sm.walkabout(self)
        raise e
        raise nodes.SkipNode
    self.body.append(self.starttag(node, 'div', CLASS='lilypond'))
    self.body.append('<p>')

    if out.score():
        if out.audio():
            self.body.append('<figure>\n')

        imgfn = copy_image_file(self.builder, node, out.score())
        self.body.append('<img class="%s" src="%s" alt="%s" />\n' %
                (_SCORE_CLASS, imgfn, self.encode(node[_LILYPOND_DOC]).strip()))

        if out.audio():
            audfn = copy_audio_file(self.builder, node, out.audio())
            self.body.append('<figcaption>\n')
            self.body.append('<audio %s class="%s" style="%s" src="%s" />\n' %
                    ('controls', _SCORE_CLASS, 'width:100%;', audfn))
            self.body.append('</figcaption>\n')
            self.body.append('</figure>\n')
            self.body.append('</div>')

        if out.audio():
            self.body.append('</figure>\n')
    else:
        # Something failed -- use text-only as a bad substitute
        self.body.append('<span class="%s">%s</span>' %
                         (_SCORE_CLASS, self.encode(node[_LILYPOND_DOC]).strip()))
    self.body.append('</p>')
    raise nodes.SkipNode


def setup(app):
    app.add_node(lilypond_inline_node, html=(html_visit_lilypond_inline_node, None))
    app.add_node(lilypond_outline_node, html=(html_visit_lilypond_outline_node, None))
    app.add_role('lily', lilypond_role)
    app.add_directive('lily', LilyPondDirective)

    app.add_config_value('lilypond_lilypond_args', ['lilypond'], '')
    app.add_config_value('lilypond_timidity_args', ['timidity'], '')
    app.add_config_value('lilypond_magick_home', '', '')
