#!/usr/bin/env python3


class Color:

    def __init__(self, string):
        self.str = string

    def green(self):
        return f"\033[0;32m{self.str}\033[0;0m"

    def yellow(self):
        return f"\033[0;33m{self.str}\033[0;0m"

    def red(self):
        return f"\033[0;31m{self.str}\033[0;0m"

    def blue(self):
        return f"\033[0;34m{self.str}\033[0;0m"

    def gray(self):
        return f"\033[2;37m{self.str}\033[0;0m"

    def bold_green(self):
        return f"\033[1;32m{self.str}\033[0;0m"

    def bold_yellow(self):
        return f"\033[1;33m{self.str}\033[0;0m"

    def bold_red(self):
        return f"\033[1;31m{self.str}\033[0;0m"

    def bold_blue(self):
        return f"\033[1;34m{self.str}\033[0;0m"
