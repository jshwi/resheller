#!/usr/bin/env python3
"""setup.py"""

from setuptools import setup, find_packages

with open("README.md", "r") as readme:
    README = readme.read()


setup(
    name='resheller',
    version="1.0.0",
    description="Reverse shell server",
    long_description=README,
    url="https://github.com/jshwi/resheller",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    license='MIT',
    author='Stephen Whitlock',
    author_email='stephen@jshwisolutions.com',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    install_requires=[
        "mss==4.0.3",
        "object-colors==1.0.3",
        "pynput==1.4.2",
        "requests==2.22.0",
        "PyInstaller==3.5",
        "root-finder==1.0.1"
    ],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "server=bin.server",
            "client=bin.client",
            "build=bin.build",
        ],
    },
)
