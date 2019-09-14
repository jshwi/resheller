#!/usr/bin/env python3
from os import name
from subprocess import call

from src.stdout.color import Color


class Title:

    def __init__(self):
        self.icon = Color("{[<>]}").b_blu()

    @staticmethod
    def clear_screen():
        clear = "clear"
        if name == "nt":
            clear = "cls"
        call(clear, shell=True)

    def resheller(self):
        print(Color(f"          , .  ^  . ,    ").b_blu())
        print(Color(f"      .++._,_.,+,._,_.++.").b_blu())
        print(f"     {self.icon}{Color('RESHELLER').b_red()}{self.icon}")
        print(Color(f"     `+~~`~~+~~^~~+~~`~~+`").b_blu())

    def header(self):
        header = Color('CONTROLCENTRE').b_grn()
        print(
            f"{self.icon}   {header}   {self.icon}")
