#!/usr/bin/env python3
"""setup.py"""

from setuptools import setup, find_packages

with open("README.md", "r") as readme:
    README = readme.read()


setup(
    name='resheller',
    version='2019.9',
    packages=find_packages(),
    url="https://github.com/jshwi/resheller",
    license='MIT',
    author='Stephen Whitlock',
    author_email='stephen@jshwisolutions.com',
    description='',
    long_description=README,
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "mss==4.0.3",
        "pynput==1.4.2",
        "requests==2.22.0",
        "PyInstaller==3.5",
    ]
)
