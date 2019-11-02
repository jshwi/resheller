#!/usr/bin/env python3
from os import name
from subprocess import call

from object_colors import Color


def usage(session: bool = False, keylogger: bool = False) -> str:
    if session:
        stdout = (
            "targets          --> view available targets\n"
            "session <number> --> select target by index\n"
        )

    elif not session and keylogger:
        stdout = (
            "keylogger <opt>    --> <start> --> start keylogger on target\n"
            "                       <dump>  --> retrieve logs from target\n"
        )
    else:
        stdout = (
            "help            --> print this help message\n"
            "download <path> --> download file from target\n"
            "upload <path>   --> upload file from target\n"
            "get <url>       --> download file from website to target\n"
            "screenshot      --> take screenshot on target\n"
            "check           --> check for admin privileges\n"
            "keylogger <opt> --> <start> --> start keylogger on target\n"
            "                    <dump>  --> retrieve logs from target\n"
            "quit            --> exit reverse shell\n"
        )
    return f"[*] Usage:\n\n{stdout}"


def colors() -> Color:
    return Color(
        ylw={"text": "yellow"},
        grn={"text": "green"},
        red={"text": "red"},
        b_grn={"text": "green", "effect": "bold"},
        b_red={"text": "red", "effect": "bold"},
        b_blu={"text": "blue", "effect": "bold"},
    )


color = colors()


class Title:

    def __init__(self) -> None:
        self.icon = color.b_blu.get("{[<>]}")

    @staticmethod
    def clear_screen() -> None:
        clear = "clear"
        if name == "nt":
            clear = "cls"
        call(clear, shell=True)

    def resheller(self) -> None:
        color.b_blu.print("          , .  ^  . ,    ")
        color.b_blu.print("      .++._,_.,+,._,_.++.")
        print(f"     {self.icon}{color.b_red.get('RESHELLER')}{self.icon}")
        color.b_blu.print(f"     `+~~`~~+~~^~~+~~`~~+`")

    def header(self) -> None:
        header = color.b_grn.get('CONTROLCENTRE')
        print(f"{self.icon}   {header}   {self.icon}")
