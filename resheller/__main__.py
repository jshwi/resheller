#!/usr/bin/env python3
__author__ = "Stephen Whitlock"
__copyright__ = "Copyright 2019, Jshwi Solutions"
__license__ = "MIT"
__version__ = "2019.09"
__maintainer__ = "Stephen Whitlock"
__email__ = "stephen@jshwisolutions.com"
__status__ = "Production"
from src.stdout.title import Title
from src.server.server import Server


def main():
    title = Title()
    server = Server()
    title.clear_screen()
    title.title()
    server.sock_object()
    server.thread()
    title.header()
    server.control_centre()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        exit(0)
