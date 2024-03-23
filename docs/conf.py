# This file is generated from sphinx-notes/cookiecutter.
# You need to consider modifying the TEMPLATE or modifying THIS FILE.

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# -- Project information -----------------------------------------------------

project = 'sphinxnotes-lilypond'
author = 'Shengyu Zhang'
copyright = "2023, " + author

# The full version, including alpha/beta/rc tags
version = release = '2.1'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.githubpages',
    'sphinx_design',
    'sphinx_copybutton',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The document name of the “master” document, that is,
# the document that contains the root toctree directive.
# Default is 'index', we set it here for supporting Sphinx<2.0
master_doc = 'index'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# A boolean that decides whether codeauthor and sectionauthor directives
# produce any output in the built files.
show_authors = True

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'furo'

html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
html_theme_options = {
    "source_repository": "https://github.com/sphinx-notes/lilypond/",
    "source_branch": "master",
    "source_directory": "docs/",
}

# The URL which points to the root of the HTML documentation.
# It is used to indicate the location of document like canonical_url
html_baseurl = 'https://sphinx.silverrainz.me/lilypond'

html_logo = html_favicon = '_static/sphinx-notes.png'

# -- Extensions -------------------------------------------------------------

#
extensions.append('sphinxnotes.any')
from sphinxnotes.any import Schema, Field as F
#
version_schema = Schema('version',
                        name=F(unique=True, referenceable=True, required=True, form=F.Form.LINES),
                        attrs={'date': F(referenceable=True)},
                        content=F(form=F.Form.LINES),
                        description_template=open('_templates/version.rst', 'r').read(),
                        reference_template='🏷️{{ title }}',
                        missing_reference_template='🏷️{{ title }}',
                        ambiguous_reference_template='🏷️{{ title }}')
confval_schema = Schema('confval',
                        name=F(unique=True, referenceable=True, required=True, form=F.Form.LINES),
                        attrs={
                            'type': F(),
                            'default': F(),
                            'choice': F(form=F.Form.WORDS),
                            'versionadded': F(),
                            'versionchanged': F(form=F.Form.LINES),
                        },
                        content=F(),
                        description_template=open('_templates/confval.rst', 'r').read(),
                        reference_template='⚙️{{ title }}',
                        missing_reference_template='⚙️{{ title }}',
                        ambiguous_reference_template='⚙️{{ title }}')
example_schema = Schema('example',
                        name=F(referenceable=True),
                        attrs={'style': F()},
                        content=F(form=F.Form.LINES),
                        description_template=open('_templates/example.rst', 'r').read(),
                        reference_template='📝{{ title }}',
                        missing_reference_template='📝{{ title }}',
                        ambiguous_reference_template='📝{{ title }}')
#
any_schemas = [
    version_schema,
    confval_schema,
    example_schema,
]
primary_domain = 'any'
#

extensions.append('sphinx.ext.extlinks')
extlinks = {
    'issue': ('https://github.com/sphinx-notes/lilypond/issues/%s', '💬%s'),
    'pull': ('https://github.com/sphinx-notes/lilypond/pull/%s', '🚀%s'),
    'tag': ('https://github.com/sphinx-notes/lilypond/releases/tag/%s', '🏷️%s'),
}

extensions.append('sphinxcontrib.gtagjs')
gtagjs_ids = ['G-E4SNX0WZYV']

#
# -- Eat your own dog food --------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath('../src/sphinxnotes'))
extensions.append('lilypond')

# DOG FOOD CONFIGURATION START

# Use a more relevant example emoji.
example_schema.reference_template = '🎵 ' + example_schema.reference_template[1:]
example_schema.missing_reference_template = '🎵 ' + example_schema.missing_reference_template[1:]
example_schema.ambiguous_reference_template = '🎵 ' + example_schema.ambiguous_reference_template[1:]

# DOG FOOD CONFIGURATION END
