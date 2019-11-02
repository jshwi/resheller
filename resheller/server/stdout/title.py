#!/usr/bin/env python3
from os import name
from subprocess import call

from src.stdout.colors import color


class Title:

    def __init__(self):
        self.icon = color.b_blu.get("{[<>]}")

    @staticmethod
    def clear_screen():
        clear = "clear"
        if name == "nt":
            clear = "cls"
        call(clear, shell=True)

    def resheller(self):
        color.b_blu.print("          , .  ^  . ,    ")
        color.b_blu.print("      .++._,_.,+,._,_.++.")
        print(f"     {self.icon}{color.b_red.get('RESHELLER')}{self.icon}")
        color.b_blu.print(f"     `+~~`~~+~~^~~+~~`~~+`")

    def header(self):
        header = color.b_grn.get('CONTROLCENTRE')
        print(f"{self.icon}   {header}   {self.icon}")
