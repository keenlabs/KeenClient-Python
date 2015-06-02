#!/usr/bin/env python

from setuptools import setup
import os, sys

setup_path = os.path.dirname(__file__)
reqs_file = open(os.path.join(setup_path, 'requirements.txt'), 'r')
reqs = reqs_file.readlines()
reqs_file.close()

tests_require = ['nose', 'mock']

if sys.version_info < (2, 7):
    tests_require.append('unittest2')

setup_requires = []
if 'nosetests' in sys.argv[1:]:
    setup_requires.append('nose')

setup(
    name="keen",
    version="0.3.14",
    description="Python Client for Keen IO",
    author="Keen IO",
    author_email="team@keen.io",
    url="https://github.com/keenlabs/KeenClient-Python",
    packages=["keen"],
    install_requires=reqs,
    tests_require=tests_require,
    test_suite='nose.collector',
)
