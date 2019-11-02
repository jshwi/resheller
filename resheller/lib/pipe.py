#!/usr/bin/env python3
from json import loads, dumps
from socket import socket


class SafeSocket:

    def __init__(self, sock: socket) -> None:
        self.sock = sock

    def send(self, data: str) -> None:
        json_data = dumps(data)
        self.sock.send(json_data.encode('utf-8'))

    def recv(self) -> str:
        data = "".encode('utf-8')
        while True:
            try:
                data = data + self.sock.recv(1024)
                return loads(data)
            except ValueError:
                continue

    def callback(self, data: str) -> str:
        self.send(data)
        return self.recv()
