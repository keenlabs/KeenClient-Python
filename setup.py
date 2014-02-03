#!/usr/bin/env python
import os
from setuptools import setup, find_packages

def fpath(name):
    return os.path.join(os.path.dirname(__file__), name)

def read(fname):
    return open(fpath(fname)).read()

def desc():
    info = ''
    try:
        return read('README.md')
    except IOError:
        return info

setup(
    name="keen",
    version="0.2.3",
    license='MIT',
    description="Python Client for Keen IO",
    long_description=desc(),
    author="Keen IO",
    author_email="team@keen.io",
    url="https://github.com/keenlabs/KeenClient-Python",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        "requests",
        "pycrypto",
        "Padding"
    ],
    tests_require=[
        "nose"
    ],
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