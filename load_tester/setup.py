# setup.py
# This script is used to package and install the `barazmoon` load testing module.
# It defines package metadata and dependencies.
import os
from setuptools import setup, find_packages


# Read the contents of the README.md file for the long description of the package
def read():
    return open(os.path.join(os.path.dirname(__file__), "README.md")).read()


# Define the package configuration using setuptools
setup(
    name="barazmoon",
    version="0.0.1",
    keywords=["load testing", "web service", "restful api"],
    packages=find_packages("."),
    long_description=read(),
    install_requires=[
        "numpy==1.26.3",
        "aiohttp==3.9.5",
    ]
)
