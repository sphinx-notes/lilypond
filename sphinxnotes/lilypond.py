# -*- coding: utf-8 -*-
"""
    Sphinx Extension for LilyPond
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Allow LilyPond music notes to be included in Sphinx-generated documents
    inline and outline.

    :copyright: Copyright ©2020 by Shengyu Zhang.
    :copyright: Copyright ©2009 by Wei-Wei Guo.
    :license: BSD, see LICENSE for details.

    The extension is modified from mathbase.py and pngmath.py by Sphinx team.
"""

import shutil
import posixpath
import tempfile
from os import path
from hashlib import sha1 as sha
from abc import abstractmethod

from docutils import nodes
from docutils.utils import unescape
from docutils.parsers.rst import directives, Directive
from sphinx.util import ensuredir, relative_uri
from sphinx.config import Config
from sphinx.errors import SphinxError

from sphinxnotes import lilyport

_DIVCLS = 'lilypond'
_SCORECLS = 'lilypond-score'
_AUDIOCLS = 'lilypond-audio'

class LilyError(SphinxError):
    category = 'LilyPond extension error'

class lily_inline_node(nodes.Inline, nodes.TextElement): pass

class lily_outline_node(nodes.Part, nodes.Element): pass

def lily_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    node = lily_inline_node()
    node['docname'] = inliner.document.settings.env.docname
    node['rawtext'] = rawtext
    node['lilysrc'] = unescape(text, restore_backslashes=True)
    node['preview'] = True
    return [node], []

class BaseLilyDirective(Directive):

    optional_arguments = 6
    option_spec = {
        'crop': directives.flag,
        'audio': directives.unchanged, # control, autoplay,
        'transpose': directives.unchanged,
        'noheader': directives.flag,
        'nofooter': directives.flag,
        'preview': directives.flag,
    }


    @abstractmethod
    def read_lily_source(self, node: nodes.Node):
        raise NotImplementedError()


    def run(self):
        node = lily_outline_node()
        node['docname'] = self.state.document.settings.env.docname
        node['rawtext'] = self.block_text
        node['lilysrc'] = self.read_lily_source()
        node['crop'] = 'crop' in self.options
        node['audio'] = self.options.get('audio')
        node['transpose'] = self.options.get('transpose')
        node['noheader'] = 'noheader' in self.options
        node['nofooter'] = 'nofooter' in self.options
        node['preview'] = 'preview' in self.options
        return [node]

class LilyDirective(BaseLilyDirective):

    has_content = True

    def read_lily_source(self) -> str:
        return '\n'.join(self.content)


class LilyIncludeDirective(BaseLilyDirective):

    required_arguments = 1
    final_argument_whitespace = True

    def read_lily_source(self) -> str:
        lilyfn = self.arguments[0]
        if not path.isabs(lilyfn):
            # Rel to abs
            env = self.state.document.settings.env
            lilyfn = path.join(path.dirname(env.doc2path(env.docname)), lilyfn)
        with open(lilyfn, 'r') as f:
            return f.read()

def hash_node(node) -> str:
    return sha((node['lilysrc'] + node['rawtext']).encode('utf-8')).hexdigest()

def copy_file(builder, node, srcfn:str, destdir:str) -> str:
    '''Copy file srcfn to builder's outdir, return a relative path to current
    document. If the file already exists in destdir, just return the relative path.
    '''
    _, ext = path.splitext(srcfn)
    sig = hash_node(node) + ext
    outfn = path.join(builder.outdir, destdir, 'lilypond', sig)
    reluri = relative_uri(builder.get_target_uri(node['docname']), destdir)
    relfn = posixpath.join(reluri, 'lilypond', sig)
    if path.isfile(outfn):
        return relfn
    ensuredir(path.dirname(outfn))
    shutil.copyfile(srcfn, outfn)
    return relfn


def copy_image_file(builder, node, imgfn:str) -> str:
    return copy_file(builder, node, imgfn, '_images')


def copy_audio_file(builder, node, audfn:str) -> str:
    return copy_file(builder, node, audfn, '_audio')


def create_document(config: Config, node: nodes.Node) -> lilyport.Document:
    return lilyport.Document(node['lilysrc'],
            lilypond_args = config.lilypond_lilypond_args,
            timidity_args = config.lilypond_timidity_args,
            magick_home = config.lilypond_magick_home)


# TODO: two type
def html_visit_lily_node(self, node:lily_outline_node):
    doc = create_document(self.builder.config, node)
    outdir = self.builder.config.lilypond_builddir or tempfile.mkdtemp(
            prefix='sphinxnotes-lilypond')
    out:lilyport.Output = None
    try:
        if node.get('transpose'):
            from_pitch, to_pitch = node['transpose'].split(' ', maxsplit=1)
            doc.transpose(from_pitch, to_pitch)
        if node.get('audio'): # TODO
            doc.enable_audio_output()
        doc.strip_header_footer(
                strip_header=node.get('noheader'),
                strip_footer=node.get('nofooter'))
        out = doc.output(outdir,
                crop=node.get('crop'),
                preview=node.get('preview'))
    except lilyport.Error as e:
        sm = nodes.system_message(e, type='WARNING', level=2,
                                  backrefs=[], source=node['lilysrc'])
        sm.walkabout(self)
        raise nodes.SkipNode

    # Create div for block level element
    if isinstance(node, lily_outline_node):
        self.body.append(self.starttag(node, 'div', CLASS='lilypond'))
        self.body.append('<p>')

    if out.audio:
        self.body.append('<figure style="display:table;">\n')

    # TODO: standalone css
    if out.preview:
        imgfn = copy_image_file(self.builder, node, out.preview)
        self.body.append(
            '<img class="%s" src="%s" alt="%s" align="absbottom"/>' %
            (_SCORECLS, imgfn, self.encode(out.source).strip()))
    elif out.score:
        imgfn = copy_image_file(self.builder, node, out.score)
        self.body.append('<img class="%s" src="%s" alt="%s"/>\n' %
                (_SCORECLS, imgfn, self.encode(out.source).strip()))
    elif out.paged_scores:
        for p in out.paged_scores:
            imgfn = copy_image_file(self.builder, node, p)
            self.body.append('<img class="%s" src="%s" alt="%s"/>\n' %
                    (_SCORECLS, imgfn, self.encode(out.source).strip()))
    else:
        # TODO
        sm = nodes.system_message('No score generated', type='WARNING', level=2,
                                  backrefs=[], source=node['lilysrc'])
        sm.walkabout(self)
        raise nodes.SkipNode

    if out.audio:
        audfn = copy_audio_file(self.builder, node, out.audio)
        self.body.append('<figcaption style="display:table-caption; caption-side:bottom; padding:10px">\n')
        self.body.append('<audio %s class="%s" style="%s" src="%s" />\n' %
                ('controls', _SCORECLS, 'width:100%;', audfn))
        self.body.append('</figcaption>\n')
        self.body.append('</figure>\n')

    if isinstance(node, lily_outline_node):
        self.body.append('</p>')
        self.body.append('</div>')

    raise nodes.SkipNode


def setup(app):
    app.add_node(lily_inline_node, html=(html_visit_lily_node, None))
    app.add_node(lily_outline_node, html=(html_visit_lily_node, None))
    app.add_role('lily', lily_role)
    app.add_directive('lily', LilyDirective)
    app.add_directive('lilyinclude', LilyIncludeDirective)

    app.add_config_value('lilypond_lilypond_args', ['lilypond'], '')
    app.add_config_value('lilypond_timidity_args', ['timidity'], '')
    app.add_config_value('lilypond_magick_home', None, '')
    app.add_config_value('lilypond_builddir', None, '')
    # TODO: Font size
