#!/usr/bin/env python3
"""main"""
from src.build.parser import parser
from src.build import build
from src.server import server


def main():
    """if user runs server --build/-b build the client
    If no arguments run the server
    """
    args = parser()
    if args.build:
        build.main()
    else:
        server.main()
