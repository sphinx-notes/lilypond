# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from doc import project

with open('doc/desc.rst') as f:
    long_desc = f.read()

setup(
    name=project.name,
    version=project.version,
    url=project.url,
    download_url=project.download_url,
    license=project.license,
    author=project.author,
    description=project.description,
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
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
    keywords=project.keywords,
    platforms='any',
    python_requires='>=3',
    packages=find_packages(),
    include_package_data=True,
    # sphinx.util.compat.Directive class is now deprecated in 1.6
    install_requires= ['Sphinx>=1.6', 'python-ly', 'wand'],
    namespace_packages=['sphinxnotes'],
)
