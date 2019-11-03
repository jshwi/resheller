#!/usr/bin/env python3
"""stdout"""
from os import name
from subprocess import call

from object_colors import Color


COLOR = Color(
    ylw={"text": "yellow"},
    grn={"text": "green"},
    red={"text": "red"},
    b_grn={"text": "green", "effect": "bold"},
    b_red={"text": "red", "effect": "bold"},
    b_blu={"text": "blue", "effect": "bold"},
)


def usage(session: bool = False, keylogger: bool = False) -> str:
    """Return various forms of usage for given function

    :param session:     View usage for a new session
    :param keylogger:   View usage for using the keylogger
    :return:            Output of the usage depending on boolean
    """
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


class Title:
    """Set parameters for stylized module title"""

    def __init__(self) -> None:
        self.icon = COLOR.b_blu.get("{[<>]}")

    @staticmethod
    def clear_screen() -> None:
        """Run clear screen tailored for Windows and Linux"""
        clear = "clear"
        if name == "nt":
            clear = "cls"
        call(clear, shell=True)

    def resheller(self) -> None:
        """Print the title"""
        COLOR.b_blu.print("          , .  ^  . ,    ")
        COLOR.b_blu.print("      .++._,_.,+,._,_.++.")
        print(f"     {self.icon}{COLOR.b_red.get('RESHELLER')}{self.icon}")
        COLOR.b_blu.print(f"     `+~~`~~+~~^~~+~~`~~+`")

    def header(self) -> None:
        """Print the control centre header"""
        header = COLOR.b_grn.get("CONTROLCENTRE")
        print(f"{self.icon}   {header}   {self.icon}")
