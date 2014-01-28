#!/usr/bin/env python
""" Basic Setup Script """

from setuptools import setup

setup(
    name='gabay-vsvbp',
    version='0.0.1',
    description='Variable Sized Vector Packing Heuristics',
    author='Michael Gabay',
    author_email='',
    packages=['vsvbp'],
    scripts=['vsvbp-benchmark'],
    url='',
    license='',
    long_description=open('../../README.md').read(),
    keywords='',
    use_2to3 = True,
    classifiers=[
      'Development Status :: 1 - Planning',
      'Intended Audience :: Science/Research',
      'Topic :: Scientific/Engineering'
    ],
)
