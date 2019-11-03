#!/usr/bin/env python3
from os import name
from subprocess import call


class Clean:
    def __init__(self):
        self.windows = True if name == "nt" else False
        self.cruft = {
            "rm": ["build", "dist"],
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
                "__pycache__",
            ],
        }

    def clean_linux(self):
        for key, values in self.cruft.items():
            for val in values:
                if key == "rm":
                    call(f"rm -rf {val}", shell=True)
                else:
                    call("find . -name %s -exec rm -rf {} +" % val, shell=True)
