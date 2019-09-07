#!/usr/bin/env python3


class Color:

    def __init__(self, string):
        self.str = string

    def grn(self):
        return f"\033[0;32m{self.str}\033[0;0m"

    def ylw(self):
        return f"\033[0;33m{self.str}\033[0;0m"

    def red(self):
        return f"\033[0;31m{self.str}\033[0;0m"

    def b_grn(self):
        return f"\033[1;32m{self.str}\033[0;0m"

    def b_red(self):
        return f"\033[1;31m{self.str}\033[0;0m"

    def b_blu(self):
        return f"\033[1;34m{self.str}\033[0;0m"
