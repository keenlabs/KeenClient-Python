#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Fix for older setuptools
import re
import os

from setuptools import setup, find_packages


def fpath(name):
    return os.path.join(os.path.dirname(__file__), name)


def read(fname):
    return open(fpath(fname)).read()


def desc():
    info = read('README.md')
    try:
        return info + '\n\n' + read('CHANGES.md')
    except IOError:
        return info


# grep keen/__init__.py since python 3.x cannot import it before using 2to3
file_text = read(fpath('keen/__init__.py'))
def grep(attrname):
    pattern = r"{0}\W*=\W*'([^']+)'".format(attrname)
    strval, = re.findall(pattern, file_text)
    return strval


def strip_comments(l):
    return l.split('#', 1)[0].strip()


def reqs(*f):
    return [
        r for r in (
            strip_comments(l) for l in open(
                os.path.join(os.getcwd(), *f)).readlines()
        ) if r]

install_requires = reqs('requirements.txt')
tests_require = reqs('requirements-test.txt')

setup(
    name="keen",
    version=grep('__version__'),
    license=grep('__license__'),
    author=grep('__author__'),
    description="Python Client for Keen IO",
    long_description=desc(),
    author_email="team@keen.io",
    url="https://github.com/keenlabs/KeenClient-Python",
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=install_requires,
    tests_require=tests_require,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    test_suite='nose.collector'
)
