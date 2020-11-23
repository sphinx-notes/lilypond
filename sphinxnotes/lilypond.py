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

from docutils import nodes, utils
from docutils.parsers.rst import directives
from sphinx.util.compat import Directive
from sphinx.util import ensuredir

from sphinxnotes import binding

class lilypond_inline_node(nodes.Inline, nodes.TextElement): pass

class lilypond_outline_node(nodes.Part, nodes.Element): pass

def lilypond_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    music = utils.unescape(text, restore_backslashes=True)
    return [lilypond_inline_node(music=music)], []

class LilyPondDirective(Directive):

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        'crop': directives.flag,
        'audio': directives.unchanged,
    }

    def run(self):
        music = '\n'.join(self.content)
        node = lilypond_outline_node()
        node['music'] = music
        node['docname'] = self.state.document.settings.env.docname
        return [node]

def render_lilypond_document(self, music:str):
    """
    Render the Lilypond music expression *lily* using lilypond.
    """
    shasum = "%s" % sha(music.encode('utf-8')).hexdigest()
    relfn = posixpath.join(self.builder.imgpath, 'sphinxnotes-lilypond', shasum)
    outfn = path.join(self.builder.outdir, '_images', 'sphinxnotes-lilypond', shasum)
    if path.isfile(outfn):
        return relfn
    ensuredir(path.dirname(outfn))

    doc = binding.Document(music)
    out = doc.output()
    shutil.copyfile(out.score(), outfn)
    out.cleanup()

    return relfn

def html_visit_lilypond_inline_node(self, node):
    music = node['music']
    try:
        fname = render_lilypond_document(self, music)
    except binding.LilyPondDocumentError as e:
        sm = nodes.system_message(e, type='WARNING', level=2,
                                  backrefs=[], source=node['music'])
        sm.walkabout(self)
        raise nodes.SkipNode
    if fname is None:
        # something failed -- use text-only as a bad substitute
        self.body.append('<span class="sphinxcontrib-lilypond">%s</span>' %
                         self.encode(node['music']).strip())
    else:
        self.body.append(
            '<img class="sphinxcontrib-lilypond" src="%s" alt="%s" align="absbottom"/>' %
            (fname, self.encode(node['music']).strip()))
    raise nodes.SkipNode


def html_visit_lilypond_outline_node(self, node):
    music = node['music']
    try:
        fname = render_lilypond_document(self, music)
    except binding.LilyPondDocumentError as e:
        sm = nodes.system_message(e, type='WARNING', level=2,
                                  backrefs=[], source=node['music'])
        sm.walkabout(self)
        self.builder.warn('inline lilypond %r: ' % node['music'] + e)
        raise nodes.SkipNode
    self.body.append(self.starttag(node, 'div', CLASS='lily'))
    self.body.append('<p>')
    if fname is None:
        # Something failed -- use text-only as a bad substitute
        self.body.append('<span class="sphinxnotes-lilypond">%s</span>' %
                         self.encode(node['music']).strip())
    else:
        self.body.append('<img src="%s" alt="%s" />\n</div>' %
                         (fname, self.encode(node['music']).strip()))
    self.body.append('</p>')
    raise nodes.SkipNode


def setup(app):
    app.add_node(lilypond_inline_node, html=(html_visit_lilypond_inline_node, None))
    app.add_node(lilypond_outline_node, html=(html_visit_lilypond_outline_node, None))
    app.add_role('ly', lilypond_role)
    app.add_directive('ly', LilyPondDirective)
