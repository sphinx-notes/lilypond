# -*- coding: utf-8 -*-
"""
    sphinxnotes.lilypond
    ~~~~~~~~~~~~~~~~~~~~

    Sphinx extension for embedding LilyPond scores.

    :copyright: Copyright 2021 by the Shengyu Zhang.
    :license: BSD, see LICENSE for details.
"""

import shutil
import posixpath
import tempfile
from os import path
from hashlib import sha1 as sha
from abc import abstractmethod
from typing import Tuple

from docutils import nodes
from docutils.utils import unescape
from docutils.parsers.rst import directives, Directive

from sphinx.util import ensuredir, relative_uri, logging
from sphinx.config import Config

from . import lilypond

__title__= 'sphinxnotes-lilypond'
__license__ = 'BSD'
__version__ = '1.3'
__author__ = 'Shengyu Zhang'
__url__ = 'https://sphinx-notes.github.io/lilypond'
__description__ = 'Sphinx extension for Lilypond'
__keywords__ = 'documentation, music, sphinx, lilypond, extension'

logger = logging.getLogger(__name__)

_DIVCLS = 'lilypond'
_SCORECLS = 'lilypond-score'
_AUDIOCLS = 'lilypond-audio'
_LILYDIR = '_lilypond'

class lily_base_node(object):
    """
    Parent class of :class:`lily_inline_node` and :class:`lily_outline_node`,
    just created for type annotations.
    """
    pass

class lily_inline_node(nodes.Inline, nodes.TextElement, lily_base_node): pass

class lily_outline_node(nodes.Part, nodes.Element, lily_base_node): pass

def lily_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    node = lily_inline_node()
    node['docname'] = inliner.document.settings.env.docname
    node['rawtext'] = rawtext
    node['lilysrc'] = unescape(text, restore_backslashes=True)
    node['noedge'] = True
    node['preview'] = True
    return [node], []


def top_or_bottom(argument:str) -> str:
    return directives.choice(argument, ('top', 'bottom'))

class BaseLilyDirective(Directive):

    option_spec = {
        'noheader': directives.flag,
        'nofooter': directives.flag,
        'noedge': directives.flag,
        'preview': directives.flag,
        'audio': directives.flag,
        'loop': directives.flag,
        'transpose': directives.unchanged,
        'controls': top_or_bottom,
    }


    @abstractmethod
    def read_lily_source(self) -> str:
        raise NotImplementedError()


    def run(self):
        node = lily_outline_node()
        node['docname'] = self.state.document.settings.env.docname
        node['rawtext'] = self.block_text
        node['lilysrc'] = self.read_lily_source()
        node['noheader'] = 'noheader' in self.options
        node['nofooter'] = 'nofooter' in self.options or True
        node['noedge'] = 'noedge' in self.options
        node['preview'] = 'preview' in self.options
        node['audio'] = 'audio' in self.options or 'loop' in self.options or 'controls' in self.options
        node['loop'] = 'loop' in self.options
        node['transpose'] = self.options.get('transpose')
        node['controls'] = self.options.get('controls', 'bottom')
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


def get_node_sig(node:lily_base_node) -> str:
    """Return signture of given node. """
    return sha((node['lilysrc'] + node['rawtext']).encode('utf-8')).hexdigest()


def get_builddir_and_reldir(builder, node:lily_base_node) -> Tuple[str,str]:
    """
    Return the path of Sphinx builder's outdir and its corrsponding relative
    path.
    """
    builddir = path.join(builder.outdir, _LILYDIR)
    reluri = relative_uri(builder.get_target_uri(node['docname']), '.')
    reldir = posixpath.join(reluri, _LILYDIR)
    return (builddir, reldir)


def pick_from_builddir(builder, node:lily_base_node) -> lilypond.Output:
    """
    Try to pick the LilyPond outputted files (:class:`lilypond.Output`)
    already cached in builder's outdir.
    """
    sig = get_node_sig(node)
    builddir, reldir = get_builddir_and_reldir(builder, node)
    outfn = path.join(builddir, sig)

    if not path.isdir(outfn):
        # Not in cache
        return None
    try:
        out = lilypond.Output(outfn)
    except lilypond.Error:
        logger.warning('invalid lilypond cache in %s' % outfn, location=node)
        return None
    else:
        relfn = posixpath.join(reldir, sig)
        out.relocate(relfn)
        return out


def move_to_builddir(builder, node:lily_base_node, out:lilypond.Output):
    """
    Move lilypond outputted files to builder's outdir, relocate the path of
    :class:`lilypond.Output` to relative path.
    """
    sig = get_node_sig(node)
    builddir, reldir = get_builddir_and_reldir(builder, node)
    outfn = path.join(builddir, sig)
    relfn = posixpath.join(reldir, sig)
    ensuredir(path.dirname(outfn))
    shutil.move(out.outdir, outfn)
    out.relocate(relfn)
    return out


# TODO: two type
def html_visit_lily_node(self, node:lily_base_node):
    out = pick_from_builddir(self.builder, node)

    cached = not (out is None)
    if cached:
        logger.debug('using cached result %s' % out.outdir, location=node)
    else:
        logger.debug('creating a new lilypond document', location=node)
        doc = lilypond.Document(node['lilysrc'])
        builddir = self.builder.config.lilypond_builddir or tempfile.mkdtemp(
                prefix='sphinxnotes-lilypond')
        try:
            if node.get('transpose'):
                from_pitch, to_pitch = node['transpose'].split(' ', maxsplit=1)
                doc.transpose(from_pitch, to_pitch)
            if node.get('audio'):
                doc.enable_audio_output()
            doc.strip_header_footer(
                    strip_header=node.get('noheader'),
                    strip_footer=node.get('nofooter'))
            out = doc.output(builddir, node.get('preview'), node.get('noedge'))
        except lilypond.Error as e:
            logger.warning('failed to generate scores: %s' % e, location=node)
            sm = nodes.system_message(e, type='WARNING', level=2,
                                      backrefs=[], source=node['lilysrc'])
            sm.walkabout(self)
            raise nodes.SkipNode
            # Cleanup lilypond builddir
            shutil.rmtree(builddir)
        else:
            # Get relative path
            move_to_builddir(self.builder, node, out)

    # Create div for block level element
    if isinstance(node, lily_outline_node):
        self.body.append(self.starttag(node, 'div', CLASS='lilypond'))
        self.body.append('<p>')

    if node.get('audio') and out.audio and node.get('controls') == 'top':
        self.body.append('<audio controls class="%s" style="%s" src="%s" %s>\n' %
                (_SCORECLS, 'width:100%;', out.audio, 'loop' if node.get('loop') else ''))
        self.body.append('</audio>')

    # TODO: standalone css
    if node.get('preview') and out.preview:
        self.body.append(
            '<img class="%s" src="%s" alt="%s" style="height:%s;", align="absbottom"/>' %
            (_SCORECLS,
             out.preview,
             self.encode(node['lilysrc']).strip(),
             self.builder.config.lilypond_inline_score_size))
    elif out.score:
        self.body.append('<img class="%s" src="%s" alt="%s" style="%s"/>\n' %
                (_SCORECLS, out.score, self.encode(node['lilysrc']).strip(), 'width:100%;'))
    elif out.paged_scores:
        for p in out.paged_scores:
            self.body.append('<img class="%s" src="%s" alt="%s" style="%s"/>\n' %
                    (_SCORECLS, p, self.encode(node['lilysrc']).strip(), 'width:100%;'))
    else:
        logger.warning('no score generated from lilypond document', location=node)
        sm = nodes.system_message('no score generated', type='WARNING', level=2,
                                  backrefs=[], source=node['lilysrc'])
        sm.walkabout(self)
        raise nodes.SkipNode

    if node.get('audio') and out.audio and node.get('controls') == 'bottom':
        self.body.append('<audio controls class="%s" style="%s" src="%s" %s>\n' %
                (_SCORECLS, 'width:100%;', out.audio, 'loop' if node.get('loop') else ''))
        self.body.append('</audio>')

    if isinstance(node, lily_outline_node):
        self.body.append('</p>')
        self.body.append('</div>')

    raise nodes.SkipNode

def _config_inited(app, config:Config) -> None:
    lilypond.Config.lilypond_args = config.lilypond_lilypond_args
    lilypond.Config.timidity_args = config.lilypond_timidity_args
    lilypond.Config.magick_home  = config.lilypond_magick_home

    lilypond.Config.score_format  = config.lilypond_score_format
    lilypond.Config.png_resolution  = config.lilypond_png_resolution

    lilypond.Config.audio_format  = config.lilypond_audio_format
    lilypond.Config.audio_volume = config.lilypond_audio_volume


def setup(app):
    app.add_node(lily_inline_node, html=(html_visit_lily_node, None))
    app.add_node(lily_outline_node, html=(html_visit_lily_node, None))
    app.add_role('lily', lily_role)
    app.add_directive('lily', LilyDirective)
    app.add_directive('lilyinclude', LilyIncludeDirective)

    app.add_config_value('lilypond_lilypond_args', ['lilypond'], 'env')
    app.add_config_value('lilypond_timidity_args', ['timidity'], 'env')
    app.add_config_value('lilypond_magick_home', None, 'env')
    app.add_config_value('lilypond_builddir', None, 'env')

    app.add_config_value('lilypond_score_format', 'png', 'env')
    app.add_config_value('lilypond_png_resolution', 300, 'env')
    app.add_config_value('lilypond_inline_score_size', '2.5em', 'env')

    app.add_config_value('lilypond_audio_format', 'wav', 'env')
    app.add_config_value('lilypond_audio_volume', None, 'env')

    app.connect('config-inited', _config_inited)
    # TODO: Font size
