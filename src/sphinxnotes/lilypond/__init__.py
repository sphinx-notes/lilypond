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
import re

from docutils import nodes
from docutils.utils import unescape
from docutils.parsers.rst import directives

from sphinx.util import logging
from sphinx.util.osutil import ensuredir, relative_uri
from sphinx.util.docutils import SphinxDirective
from sphinx.config import Config
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.builders.latex import LaTeXBuilder
from sphinx.environment import BuildEnvironment

from . import lilypond
from . import jianpu

logger = logging.getLogger(__name__)

_DIVCLS = 'lilypond'
_SCORECLS = 'lilypond-score'
_AUDIOCLS = 'lilypond-audio'
_LILYDIR = '_lilypond'

class lily_inline_node(nodes.Inline, nodes.TextElement): pass

class lily_outline_node(nodes.Part, nodes.Element): pass

def lily_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    env = inliner.document.settings.env # type: ignore

    if not isinstance(env.app.builder, (StandaloneHTMLBuilder, LaTeXBuilder)):
        # Builder is not supported, fallback to literal_block.
        node = nodes.literal(rawtext, unescape(text, restore_backslashes=True))
        node['docname'] = env.docname
        return [node], []

    node = lily_inline_node()
    node['docname'] = env.docname
    node['rawtext'] = rawtext
    node['lilysrc'] = r'\score{' + unescape(text, restore_backslashes=True) + '}'
    node['crop'] = True
    node['audio'] = True
    node['controls'] = 'bottom'
    return [node], []

def jianpu_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    try:
        text = jianpu.to_lilypond(unescape(text, restore_backslashes=True))
    except jianpu.Error as e:
        msg = 'failed to convert Jianpu source to LilyPond source: %s' % e
        logger.warning(msg, location=inliner.parent)
        sm = nodes.system_message(msg, type='WARNING', level=2, backrefs=[], source='')
        return [], [sm]
    return lily_role(role, rawtext, text, lineno, inliner, options, content)

def top_or_bottom(argument:str) -> str:
    return directives.choice(argument, ('top', 'bottom'))


class BaseLilyDirective(SphinxDirective):

    option_spec = {
        'nocrop': directives.flag,
        'noaudio': directives.flag,
        'loop': directives.flag,
        'transpose': directives.unchanged,
        'controls': top_or_bottom,
    }


    @abstractmethod
    def read_lily_source(self) -> str:
        raise NotImplementedError()


    def run(self) -> list[nodes.Node]:
        try:
            lilysrc = self.read_lily_source()
        except OSError as e:
            msg = 'failed to read LilyPond source: %s' % e
            logger.warning(msg, location=self.state.parent)
            sm = nodes.system_message(msg, type='WARNING', level=2, backrefs=[], source='')
            return [sm]
        except jianpu.Error as e:
            msg = 'failed to convert Jianpu source to LilyPond source: %s' % e
            logger.warning(msg, location=self.state.parent)
            sm = nodes.system_message(msg, type='WARNING', level=2, backrefs=[], source='')
            return [sm]

        if not isinstance(self.env.app.builder, (StandaloneHTMLBuilder, LaTeXBuilder)):
            # Builder is not supported, fallback to literal_block.
            node = nodes.literal_block(self.block_text, lilysrc)
            node['docname'] = self.env.docname
            return [node]

        node = lily_outline_node()
        node['docname'] = self.env.docname
        node['rawtext'] = self.block_text
        node['lilysrc'] = lilysrc
        node['audio'] = 'noaudio' not in self.options
        node['crop'] = 'nocrop' not in self.options
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
        return read_source_file(self.env, self.arguments[0])


class BaseJianpuDirective(BaseLilyDirective):

    def read_lily_source(self) -> str:
        return jianpu.to_lilypond(self.read_jianpu_source())

    @abstractmethod
    def read_jianpu_source(self) -> str:
        raise NotImplementedError()


class JianpuDirective(BaseJianpuDirective):

    has_content = True

    def read_jianpu_source(self) -> str:
        return '\n'.join(self.content)


class JianpuIncludeDirective(BaseJianpuDirective):

    required_arguments = 1
    final_argument_whitespace = True

    def read_jianpu_source(self) -> str:
        return read_source_file(self.env, self.arguments[0])


def get_node_sig(node:lily_inline_node|lily_outline_node) -> str:
    """Return signture of given node. """
    return sha((node['lilysrc'] + node['rawtext']).encode('utf-8')).hexdigest()


def get_builddir_and_reldir(builder, node:lily_inline_node|lily_outline_node) -> tuple[str,str]:
    """
    Return the path of Sphinx builder's outdir and its corrsponding relative
    path.
    """
    builddir = path.join(builder.outdir, _LILYDIR)
    reluri = relative_uri(builder.get_target_uri(node['docname']), '.')
    reldir = posixpath.join(reluri, _LILYDIR)
    return (builddir, reldir)


def pick_from_builddir(builder, node:lily_inline_node|lily_outline_node) -> lilypond.Output|None:
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


def move_to_builddir(builder, node:lily_inline_node|lily_outline_node, out:lilypond.Output):
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


def get_lilypond_output(self, node:lily_inline_node|lily_outline_node) -> lilypond.Output:
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
            out = doc.output(builddir, node.get('crop'))
        except lilypond.Error as e:
            logger.warning('failed to generate scores: %s' % e, location=node)
            sm = nodes.system_message(e, type='WARNING', level=2,
                                      backrefs=[], source=node['lilysrc'])
            sm.walkabout(self)
            shutil.rmtree(builddir) # cleanup lilypond builddir
            raise nodes.SkipNode
        else:
            # Get relative path
            move_to_builddir(self.builder, node, out)
    return out


def html_visit_lily_node(self, node:lily_inline_node|lily_outline_node):
    # Helper to append a audio player.
    def append_audio():
        if isinstance(node, lily_inline_node):
            size, unit = parse_html_size(self.builder.config.lilypond_inline_score_size)
            style = 'width: %s%s;' % (1.2*size, unit)
        else:
            style = 'width:100%;'
        self.body.append('<audio controls class="%s" style="%s" src="%s" %s>\n' %
                (_AUDIOCLS, style, out.audio, 'loop' if node.get('loop') else ''))
        self.body.append('</audio>')

    out = get_lilypond_output(self, node)

    # Create div for block element and span for inline element.
    if isinstance(node, lily_outline_node):
        self.body.append(self.starttag(node, 'div', CLASS=_DIVCLS))
        self.body.append('<p>')
    else:
        self.body.append(
            self.starttag(node, 'span', CLASS=_DIVCLS,
                          STYLE="display: inline-flex; vertical-align: middle;"))

    if node.get('audio') and out.audio and node.get('controls') == 'top':
        append_audio()

    scores = []
    score_style = ''
    if isinstance(node, lily_inline_node):
        score_style = 'height: %s;' % self.builder.config.lilypond_inline_score_size
        if out.cropped_score: # inline node MUST use cropped score
            scores.append(out.cropped_score)
    else:
        score_style = 'width: 100%;'
        if out.cropped_score:
            scores.append(out.cropped_score)
        elif out.score:
            scores.append(out.score)
        elif out.paged_scores:
            scores.extend(out.paged_scores)
    if not scores:
        raise_no_score_message_and_skip(self, node)

    for score in scores:
        self.body.append(
            '<img class="%s" src="%s" alt="%s" style="%s"/>' %
            (_SCORECLS, score, self.encode(node['lilysrc']).strip(), score_style))

    if node.get('audio') and out.audio and node.get('controls') == 'bottom':
        append_audio()

    if isinstance(node, lily_outline_node):
        self.body.append('</p>')
        self.body.append('</div>')
    else:
        self.body.append('</span>')

    raise nodes.SkipNode


def latex_visit_lily_node(self, node:lily_inline_node|lily_outline_node):
    """
    See sphinx/sphinx/writers/latex.py::visit_image().
    """

    out = get_lilypond_output(self, node)
    CR = '\n'
    options = ''

    scores = []
    is_inline = False
    if isinstance(node, lily_outline_node):
        is_inline = True
        if out.cropped_score: # inline node MUST use cropped score
            scores.append(out.cropped_score)
    else:
        if out.cropped_score:
            scores.append(out.cropped_score)
        elif out.score:
            scores.append(out.score)
        elif out.paged_scores:
            scores.extend(out.paged_scores)
    if not scores:
        raise_no_score_message_and_skip(self, node)

    for score in scores:
        if is_inline:
            self.body.append(CR)
        else:
            self.body.append(CR + r'\noindent')
        base, ext = path.splitext(score)
        self.body.append(r'\sphinxincludegraphics%s{{%s}%s}' % (options, base, ext))
        self.body.append(CR)

    if node.get('audio'):
        logger.warning('audio option is not supported for latex builder', location=node)

    raise nodes.SkipNode


def read_source_file(env:BuildEnvironment, fn:str) -> str:
    """
    Read the score source from a local file. Can be an absolute path
    (relative to the root of srcdir) or relative path (relative to the current document).
    """
    if path.isabs(fn):
        # Source dir absolute path to file system absolute path.
        #
        # Since Sphinx 7.2, env.srcdir changes its type from str to pathlib.Path.
        # See https://github.com/sphinx-doc/sphinx/pull/11526.
        #
        # TODO: Use pathlib.Path.
        #
        # NOTE: CANNOT use path.join because fn is absolute.
        # join('/foo', '/bar') finally get '/bar'.
        fn = str(env.srcdir) + fn
    else:
        # Document relative path to file system absolute path.
        fn = path.join(path.dirname(env.doc2path(env.docname)), fn)
    with open(fn, 'r') as f:
        # Febuild the current document if the file changes.
        env.note_dependency(fn)
        return f.read()


def parse_html_size(sz: str) -> tuple[float, str]:
    """Parse HTML size (like "10px", "1.2em", "100%") to number and unit."""
    regex = r'^(\d+(?:\.\d+)?)(\D+)$'
    match = re.match(regex, sz)
    if not match:
        raise ValueError("Invalid size string: %s" % sz)
    value = float(match.group(1))
    unit = match.group(2)
    return value, unit


def raise_no_score_message_and_skip(self, node):
    msg = 'no score generated'
    logger.warning(msg, location=node)
    sm = nodes.system_message(msg, type='WARNING', level=2, backrefs=[], source=node['lilysrc'])
    sm.walkabout(self)
    raise nodes.SkipNode


def _config_inited(app, config:Config) -> None:
    lilypond.Config.lilypond_args = config.lilypond_lilypond_args
    lilypond.Config.timidity_args = config.lilypond_timidity_args
    lilypond.Config.ffmpeg_args = config.lilypond_ffmpeg_args

    lilypond.Config.score_format  = config.lilypond_score_format
    lilypond.Config.png_resolution  = config.lilypond_png_resolution

    lilypond.Config.audio_format  = config.lilypond_audio_format
    lilypond.Config.audio_volume = config.lilypond_audio_volume


def setup(app):
    app.add_node(lily_inline_node,
                 html=(html_visit_lily_node, None),
                 latex=(latex_visit_lily_node, None))
    app.add_node(lily_outline_node,
                 html=(html_visit_lily_node, None),
                 latex=(latex_visit_lily_node, None))
    app.add_role('lily', lily_role)
    app.add_directive('lily', LilyDirective)
    app.add_directive('lilyinclude', LilyIncludeDirective)

    # app.add_role('jianpu', jianpu_role)
    app.add_directive('jianpu', JianpuDirective)
    app.add_directive('jianpuinclude', JianpuIncludeDirective)

    app.add_config_value('lilypond_lilypond_args', ['lilypond'], 'env')
    app.add_config_value('lilypond_timidity_args', ['timidity'], 'env')
    app.add_config_value('lilypond_ffmpeg_args', ['ffmpeg'], 'env')
    app.add_config_value('lilypond_builddir', None, 'env')

    app.add_config_value('lilypond_score_format', 'png', 'env')
    app.add_config_value('lilypond_png_resolution', 300, 'env')
    app.add_config_value('lilypond_inline_score_size', '2.5em', 'env')

    app.add_config_value('lilypond_audio_format', 'wav', 'env')
    app.add_config_value('lilypond_audio_volume', None, 'env')

    app.connect('config-inited', _config_inited)
    # TODO: Font size
