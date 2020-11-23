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
import tempfile
import posixpath
from os import path
from hashlib import sha1 as sha

from docutils import nodes, utils
from docutils.parsers.rst import directives
from sphinx.util.compat import Directive

from sphinx.errors import SphinxError
from sphinx.util import ensuredir

from sphinxnotes import binding

class lilypond_inline_node(nodes.Inline, nodes.TextElement): pass

''' What is PART '''
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
        'trim': directives.flag,
        'format': directives.unchanged,
        'audio-format': directives.unchanged,
    }

    def run(self):
        music = '\n'.join(self.content)
        node = lilypond_outline_node()
        node['music'] = music
        node['docname'] = self.state.document.settings.env.docname
        return [node]

def render_lilypond_document(self, doc:str):
    """
    Render the Lilypond music expression *lily* using lilypond.
    """
    shasum = "%s.%s" % sha(lily.encode('utf-8')).hexdigest()
    relfn = posixpath.join(self.builder.imgpath, 'lily', shasum)
    outfn = path.join(self.builder.outdir, '_images', 'lily', shasum)
    if path.isfile(outfn):
        return relfn
    # use only one tempdir per build -- the use of a directory is cleaner
    # than using temporary files, since we can clean up everything at once
    # just removing the whole directory (see cleanup_tempdir_lily)
    if not hasattr(self.builder, '_lilypng_tempdir'):
        tempdir = self.builder._lilypng_tempdir = tempfile.mkdtemp()
    else:
        tempdir = self.builder._lilypng_tempdir

    doc
    ensuredir(path.dirname(outfn))
    # use some standard lilypond arguments
    try:
        p = Popen(lilypond_args, stdout=PIPE, stderr=PIPE)
    except OSError, err:
        if err.errno != 2:   # No such file or directory
            raise
        self.builder.warn('lilypond command %r cannot be run (needed for music '
                          'display), check the pnglily_lilypond setting' %
                          self.builder.config.pnglily_lilypond)
        self.builder._lilypng_warned = True
        return None, None
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        raise LilyExtError(u'lilypond exited with error:\n[stderr]\n%s\n'
                           '[stdout]\n%s' % (stderr.decode('utf-8'), stdout.decode('utf-8')))

    shutil.copyfile(path.join(tempdir, 'music.png'), outfn)
    #Popen(['mogrify', '-trim', outfn], stdout=PIPE, stderr=PIPE)

    return relfn

def cleanup_tempdir_lily(app, exc):
    if exc:
        return
    if not hasattr(app.builder, '_lilypng_tempdir'):
        return
    try:
        shutil.rmtree(app.builder._lilypng_tempdir)
    except Exception:
        pass

def html_visit_lily(self, node):
    music = Inline_HEAD % self.builder.config.pnglily_fontsize[0]
    music += node['music'] + Inline_BACK
    #music += '#"' + node['music'] + '"' + Inline_BACK
    try:
        fname = render_lilypond_document(self, music)
    except LilyExtError, exc:
        sm = nodes.system_message(unicode(exc), type='WARNING', level=2,
                                  backrefs=[], source=node['music'])
        sm.walkabout(self)
        self.builder.warn('display lilypond %r: ' % node['music'] + unicode(exc))
        raise nodes.SkipNode
    if fname is None:
        # something failed -- use text-only as a bad substitute
        self.body.append('<span class="lily">%s</span>' %
                         self.encode(node['music']).strip())
    else:
        self.body.append(
            '<img class="lily" src="%s" alt="%s" align="absbottom"/>' %
            (fname, self.encode(node['music']).strip()))
    raise nodes.SkipNode


def html_visit_lilypond_outline_node(self, node):
    music = node['music']
    try:
        fname = render_lilypond_document(self, music)
    except LilyExtError, exc:
        sm = nodes.system_message(unicode(exc), type='WARNING', level=2,
                                  backrefs=[], source=node['music'])
        sm.walkabout(self)
        self.builder.warn('inline lilypond %r: ' % node['music'] + unicode(exc))
        raise nodes.SkipNode
    self.body.append(self.starttag(node, 'div', CLASS='lily'))
    self.body.append('<p>')
    if fname is None:
        # Something failed -- use text-only as a bad substitute
        self.body.append('<span class="lily">%s</span>' %
                         self.encode(node['music']).strip())
    else:
        self.body.append('<img src="%s" alt="%s" />\n</div>' %
                         (fname, self.encode(node['music']).strip()))
    self.body.append('</p>')
    raise nodes.SkipNode


def setup(app):
    app.add_node(lily, html=(html_visit_lily, None))
    app.add_node(lilypond_outline_node, html=(html_visit_lilypond_outline_node, None))
    app.add_role('lily', lily_role)
    app.add_directive('lily', LilyDirective)
    app.add_config_value('pnglily_preamble', '', False)
    app.add_config_value('pnglily_fontsize', ['10', '-3'], False)
    app.add_config_value('pnglily_lilypond', 'lilypond', False)
    app.add_config_value('pnglily_lilypond_args', [], False)
    app.connect('build-finished', cleanup_tempdir_lily)
