#!/usr/bin/env python3
"""parser"""
from argparse import ArgumentParser, Namespace


def parser() -> Namespace:
    """Simple parser for the build process"""
    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        "--build", "-b", action="store_true", help="build client executable"
    )
    arg_parser.add_argument(
        "--verbose", "-v", action="store_true", help="print build output"
    )
    arg_parser.add_argument(
        "--console",
        "-c",
        action="store_true",
        help="produce a client executable that also spawns a shell",
    )
    arg_parser.add_argument(
        "--keep",
        "-k",
        action="store_true",
        help="keep resulting artifacts from build",
    )
    arg_parser.add_argument(
        "--name",
        "-n",
        action="store",
        help="name of the client executable: default = client",
    )
    return arg_parser.parse_args()
