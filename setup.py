#!/usr/bin/env python

# from distutils.core import setup
from setuptools import setup, find_packages
from pip.req import parse_requirements
import pip
import sys

try:
    import multiprocessing
except ImportError:
    pass

try:
    # parse_requirements() returns generator of pip.req.InstallRequirement objects
    install_reqs = parse_requirements('requirements.txt', session=pip.download.PipSession())
except AttributeError:
    # compatibility for pip < 1.5.6
    install_reqs = parse_requirements('requirements.txt')

tests_require = ['nose', 'mock']

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in install_reqs]

if sys.version_info < (2, 7):
    tests_require.append('unittest2')

setup_requires = []
if 'nosetests' in sys.argv[1:]:
    setup_requires.append('nose')

setup(
    name="keen",
    version="0.3.13",
    description="Python Client for Keen IO",
    author="Keen IO",
    author_email="team@keen.io",
    url="https://github.com/keenlabs/KeenClient-Python",
    packages=["keen"],
    install_requires=reqs,
    tests_require=tests_require,
    test_suite='nose.collector',
)
