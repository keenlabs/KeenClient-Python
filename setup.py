#!/usr/bin/env python

from distutils.core import setup

setup(name="keen",
      version="0.1.9",
      description="Python Client for Keen IO",
      author="Keen IO",
      author_email="team@keen.io",
      url="https://github.com/keenlabs/KeenClient-Python",
      packages=["keen"],
      install_requires=["requests", "pycrypto", "Padding"],
      tests_require=["nose"]
)