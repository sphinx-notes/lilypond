# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys
import os
sys.path.insert(0, os.path.abspath('./sphinxnotes'))
import lilypond as proj

with open('README.rst') as f:
    long_desc = f.read()

setup(
    name=proj.__title__,
    version=proj.__version__,
    url=proj.__url__,
    download_url='http://pypi.python.org/pypi/' + proj.__title__,
    license=proj.__license__,
    author=proj.__author__,
    description=proj.__description__,
    long_description=long_desc,
    long_description_content_type = 'text/x-rst',
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    keywords=proj.__keywords__,
    platforms='any',
    python_requires='>=3',
    packages=find_packages(),
    include_package_data=True,
    # sphinx.util.compat.Directive class is now deprecated in 1.6
    install_requires= ['Sphinx>=1.6', 'python-ly', 'wand'],
    namespace_packages=['sphinxnotes'],
)
