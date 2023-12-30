#!/usr/bin/env python

import os
import sys
from distutils.version import LooseVersion
from setuptools import setup, find_packages

if LooseVersion(sys.version) < LooseVersion("3.8") or LooseVersion(sys.version) > LooseVersion("3.12"):
    raise RuntimeError("TTS requires python >= 3.8 and <=3.10 " "but your Python version is {}".format(sys.version))

cwd = os.path.dirname(os.path.abspath(__file__))

requirements = open(os.path.join(cwd, "requirements.txt"), "r").readlines()

with open(os.path.join(cwd, "VERSION"), "r", encoding="utf-8") as version_file:
    version = version_file.read()

with open("README.md", "r", encoding="utf-8") as readme_file:
    README = readme_file.read()
    
    
setup(
    name="DataEngine",
    version=version,
    author="Logan Hart",
    description="DataEngine is a python package for creating datasets for training deep neural networks.",
    long_description=README,
    include_package_data=True,
    long_description_content_type="text/markdown",
    packages=find_packages(include=["DataEngine", "DataEngine.*"]),
    install_requires=requirements,
    python_requires=">=3.8, <=3.12",
    zip_safe=False,
)