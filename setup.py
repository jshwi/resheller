#!/usr/bin/env python3
"""setup"""
__author__ = "Stephen Whitlock"
__copyright__ = "Copyright 2019, Jshwi Solutions"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Stephen Whitlock"
__email__ = "stephen@jshwisolutions.com"
__status__ = "Production"
from setuptools import setup, find_packages


with open("README.md", "r") as readme:
    README = readme.read()


setup(
    name="resheller",
    version="1.0.0",
    description="Reverse shell server",
    long_description=README,
    url="https://github.com/jshwi/resheller",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    license="MIT",
    author="Stephen Whitlock",
    author_email="stephen@jshwisolutions.com",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    install_requires=[
        "mss==4.0.3",
        "object-colors==1.0.3",
        "PyInstaller==3.5",
        "pynput==1.4.4",
        "pytest==5.2.2",
        "requests==2.22.0",
        "root-finder==1.0.1",
    ],
    zip_safe=True,
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "server=server:main",
            "client=resheller.client:main",
            "build=resheller.build:main",
        ]
    },
)
