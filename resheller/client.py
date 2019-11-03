#!/usr/bin/env python3
"""client"""
import sys

from resheller.src.client.main import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
