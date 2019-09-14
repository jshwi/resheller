#!/usr/bin/env python3
from os import path

from src.stdout.color import Color


class Ps1:

    def __init__(self, sock):
        self.sock = sock
        self.windows = sock.callback("get_os")
        self.req = "pwd"
        self.sep = "/"
        self.chop = 1
        self.format_os()
        self.usr = self.get_username()
        self.host = self.get_hostname()

    def get_hostname(self):
        host = self.sock.callback("hostname")
        if self.windows:
            return host[:-2]
        return host[:-1]

    def format_os(self):
        if self.windows:
            self.req = "cd"
            self.sep = "\\"
            self.chop = 2

    def get_username(self):
        usr = self.sock.callback("whoami")
        if self.windows:
            return usr.split("\\")[1][:-2]
        return usr[:-1]

    def independent_path(self, *args):
        if self.windows:
            return path.join(*args).replace("/", "\\")
        return path.join(*args)

    def resolve_path(self, root, del_, dirs, path_):
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

    def get_path(self):
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

    def prompt(self):
        path_ = self.get_path()
        ps1 = (
            f'{Color("{").b_blu()}{Color(self.usr).b_red()}'
            f'{Color("@").b_blu()}{Color(self.host).b_red()}:'
            f'{Color(path_).b_grn()}{Color("}>").b_blu()} '
        )
        cmd = input(ps1)
        if cmd == "cd" and len(cmd) == 2:
            return "cd ~"
        if cmd == "ls":
            return "dir"
        return cmd
