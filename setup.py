#!/usr/bin/env python

from distutils.core import setup

setup(name="keen",
      version="0.1.4",
      description="Python Client for Keen.io",
      author="Keen Labs",
      author_email="team@keen.io",
      url="https://github.com/keenlabs/KeenClient-Python",
      packages=["keen"],
      install_requires=["requests"],
      tests_require=["nose"]
)
