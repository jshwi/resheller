#!/usr/bin/env python3
"""ps1"""
from os import path
from typing import Union

from lib.pipe import SafeSocket
from lib.stdout import COLOR


class Ps1:
    """The prompt that will be returned from the client based on target
    machine's os i.e. Windows/Unix-Based"""

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
        """Get hostname of target machine

        :return: The target's hostname
        """
        host = self.sock.callback("hostname")
        if self.windows:
            return host[:-2]
        return host[:-1]

    def format_os(self) -> None:
        """Tailor certain items for the host machine"""
        if self.windows:
            self.req = "cd"
            self.sep = "\\"
            self.chop = 2

    def get_username(self) -> str:
        """Get the username of the target

        :return: The target's username
        """
        usr = self.sock.callback("whoami")
        if self.windows:
            return usr.split("\\")[1][:-2]
        return usr[:-1]

    def independent_path(self, *args) -> str:
        """Return path based on the target machine

        :param args:    directories
        :return:        The complete path
        """
        path_ = path.join(*args)
        if self.windows:
            return path_.replace("/", "\\")
        return path_

    def resolve_path(
        self, root: bool, del_: int, dirs: list, path_: str
    ) -> Union[str, None]:
        """Get a shorthand version of a long path

        :param root:    Boolean depending on whether the user is in root
        :param del_:    How many directories need to be "deleted" to
                        convert $HOME into ~/
        :param dirs:    List of directories in the path
        :param path_:   The real version of the path i.e.
                        /home/user/this/is/a/path
        :return:        The altered path i.e. ~/../../../path
        """
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
        return

    def get_path(self) -> str:
        """Get the path the server is in from the target machine

        :return: The path to display on the server's prompt
        """
        path_ = "~"
        stdout = self.sock.callback(self.req)
        dirs = stdout.split(self.sep)
        dirs[-1] = dirs[-1][: -self.chop]
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
        """The final item to be printed

        :return: The altered prompt or the stdout from a command
        """
        ps1 = (
            f'{COLOR.b_blu.get("{")}{COLOR.b_red.get(self.usr)}'
            f'{COLOR.b_blu.get("@")}{COLOR.b_red.get(self.host)}:'
            f'{COLOR.b_grn.get(self.get_path())}{COLOR.b_blu.get("}>")} '
        )
        cmd = input(ps1)
        if cmd == "cd" and len(cmd) == 2:
            return "cd ~"
        if cmd == "ls":
            return "dir"
        return cmd
