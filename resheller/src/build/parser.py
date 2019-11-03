#!/usr/bin/env python3
"""parser"""
from argparse import ArgumentParser, Namespace


def parser() -> Namespace:
    """Simple parser for the build process"""
    arg_parser = ArgumentParser()
    arg_parser.add_argument("--verbose", "-v", action="store_true")
    return arg_parser.parse_args()
