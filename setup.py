#!/usr/bin/env python

# from distutils.core import setup
from setuptools import setup, find_packages
import sys

try:
    import multiprocessing
except ImportError:
    pass

tests_require = ['nose']

if sys.version_info < (2, 7):
    tests_require.append('unittest2')

setup_requires = []
if 'nosetests' in sys.argv[1:]:
    setup_requires.append('nose')

setup(
    name="keen",
    version="0.3.9",
    description="Python Client for Keen IO",
    author="Keen IO",
    author_email="team@keen.io",
    url="https://github.com/keenlabs/KeenClient-Python",
    packages=["keen"],
    install_requires=["requests", "pycrypto", "Padding"],
    tests_require=tests_require,
    test_suite='nose.collector',
)
