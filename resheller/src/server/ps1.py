#!/usr/bin/env python3
"""resheller.ps1"""
from os import path

from resheller.lib.pipe import SafeSocket
from resheller.lib.stdout import color


class Ps1:

    def __init__(self, sock: SafeSocket) -> None:
        self.sock = sock
        self.windows = sock.callback("get_os")
        self.req = "pwd"
        self.sep = "/"
        self.chop = 1
        self.format_os()
        self.usr = self.get_username()
        self.host = self.get_hostname()

    def get_hostname(self) -> str:
        host = self.sock.callback("hostname")
        if self.windows:
            return host[:-2]
        return host[:-1]

    def format_os(self) -> None:
        if self.windows:
            self.req = "cd"
            self.sep = "\\"
            self.chop = 2

    def get_username(self) -> str:
        usr = self.sock.callback("whoami")
        if self.windows:
            return usr.split("\\")[1][:-2]
        return usr[:-1]

    def independent_path(self, *args) -> str:
        if self.windows:
            return path.join(*args).replace("/", "\\")
        return path.join(*args)

    def resolve_path(
            self, root: bool, del_: int, dirs: list, path_: str
    ) -> str:
        other_path = False
        home = path_ + self.sep
        if len(dirs) == 1:
            return self.sep
        if len(dirs) == 2:
            if root:
                return home
            return self.sep + dirs[1]
        if len(dirs) == 3:
            if root:
                return self.independent_path(path_, dirs[2])
            if dirs[2] == self.usr:
                return home
            del_ = 1
            other_path = True
        if len(dirs) > 3 or other_path:
            base = dirs.pop(-1)
            del dirs[0:del_]
            for _ in dirs:
                path_ = self.independent_path(path_, "..")
            return self.independent_path(path_, base)

    def get_path(self) -> str:
        path_ = "~"
        stdout = self.sock.callback(self.req)
        dirs = stdout.split(self.sep)
        dirs[-1] = dirs[-1][:-self.chop]
        if dirs[1] == self.usr:
            root, del_ = True, 2
        else:
            root = False
            if len(dirs) >= 3 and dirs[2] == self.usr:
                del_ = 3
            else:
                del_ = 1
                path_ = self.sep
        return self.resolve_path(root, del_, dirs, path_)

    def prompt(self) -> str:
        path_ = self.get_path()
        ps1 = (
            f'{color.b_blue.get("{")}{color.b_red.get(self.usr)}'
            f'{color.b_blue.get("@")}{color.b_red.get(self.host)}:'
            f'{color.b_grn.get(path_)}{color.b_blue.get("}>")} '
        )
        cmd = input(ps1)
        if cmd == "cd" and len(cmd) == 2:
            return "cd ~"
        if cmd == "ls":
            return "dir"
        return cmd
