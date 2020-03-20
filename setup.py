#!/usr/bin/env python

from setuptools import setup
import os, sys, codecs

try:
    # nose uses multiprocessing if available.
    # but setup.py atexit fails if it's loaded too late.
    # Traceback (most recent call last):
    #   File "...python2.6/atexit.py", line 24, in _run_exitfuncs
    #     func(*targs, **kargs)
    #   File "...python2.6/multiprocessing/util.py", line 258, in _exit_function
    #     info('process shutting down')
    # TypeError: 'NoneType' object is not callable
    import multiprocessing # NOQA
except ImportError:
    pass

setup_path = os.path.dirname(__file__)
reqs_file = open(os.path.join(setup_path, 'requirements.txt'), 'r')
reqs = reqs_file.readlines()
reqs_file.close()

tests_require = ['nose', 'mock', 'responses==0.5.1', 'unittest2']

setup(
    name="keen",
    version="0.6.1",
    description="Python Client for Keen IO",
    long_description=codecs.open(os.path.join('README.rst'), 'r', encoding='UTF-8').read(),
    author="Keen IO",
    author_email="team@keen.io",
    url="https://github.com/keenlabs/KeenClient-Python",
    packages=["keen"],
    install_requires=reqs,
    tests_require=tests_require,
    test_suite='nose.collector',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
