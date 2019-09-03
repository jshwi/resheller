#!/usr/bin/env python3
from os import name
from subprocess import call

from src.color import Color
from src.threaded import ThreadServer


def clear_screen():
    clear = "clear"
    if name == "nt":
        clear = "cls"
    call(clear, shell=True)


def resheller_title():
    tab = 5 * ' '
    resheller = Color('RESHELLER').bold_red()
    thing = Color("{[<>]}").bold_blue()
    clear_screen()
    print(Color(f"{tab}     , .  ^  . ,    ").bold_blue())
    print(Color(f"{tab} .++._,_.,+,._,_.++.").bold_blue())
    print(f"{tab}{thing}{resheller}{thing}")
    print(Color(f"{tab}`+~~`~~+~~^~~+~~`~~+`").bold_blue())


def reverse_shell():
    resheller_title()
    try:
        server = Server()
        server.shell()
    except OSError as err:
        print(Color(f"[!] {err}").bold_red())
        exit(0)


def main():
    resheller_title()
    centre = ThreadServer()
    centre.sock_object()
    try:
        centre.thread()
    except KeyboardInterrupt:
        exit(0)
