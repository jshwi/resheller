#!/usr/bin/env python3
"""resheller.server.main"""
from resheller.lib.stdout import Title
from resheller.src.server.server import Server


def main() -> None:
    title = Title()
    server = Server()
    title.clear_screen()
    title.resheller()
    server.sock_object()
    server.thread()
    title.header()
    server.control_centre()
