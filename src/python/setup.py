#!/usr/bin/env python
""" Basic Setup Script """

from distutils.core import setup

setup(
    name='gabay-vsvbp',
    version='0.0.1',
    author='Michael Gabay',
    author_email='',
    packages=['vsvbp'],
    scripts=['vsvbp-benchmark'],
    url='',
    license='',
    description='Variable Sized Vector Packing Heurisitcs',
    long_description=open('../../README.md').read(),
    keywords='',
    classifiers=[
      'Development Status :: 1 - Planning',
      'Intended Audience :: Science/Research',
      'Topic :: Scientific/Engineering'
    ],
)
