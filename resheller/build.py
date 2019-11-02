#!/usr/bin/env python3
"""build:main"""
import sys

from src.build.main import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
