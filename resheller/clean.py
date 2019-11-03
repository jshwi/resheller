#!/usr/bin/env python3
from os import name
from subprocess import call


def rm_items():
    """Remove Python artifacts"""
    cruft = {
        "rm": [
            "build",
            "dist",
        ],
        "find": [
            "pip-wheel-metadata",
            "htmlcov",
            "*.spec",
            ".coverage",
            "*.egg-info",
            "*.egg",
            "*.pyc",
            "*.pyo",
            "*~",
            "__pycache__"
        ],
    }
    for key, values in cruft.items():
        for value in values:
            if key == "rm":
                call(f"rm -rf {value}", shell=True)
            else:
                call("find . -name %s -exec rm -rf {} +" % value, shell=True)


def main():
    """Only run if using Linux
    .. todo::
        script an alternative for windows
    """
    if name != "nt":
        rm_items()


if __name__ == '__main__':
    main()
