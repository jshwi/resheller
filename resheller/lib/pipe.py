#!/usr/bin/env python3
from json import loads, dumps


class SafeSocket:

    def __init__(self, sock):
        self.sock = sock

    def send(self, data):
        json_data = dumps(data)
        self.sock.send(json_data.encode('utf-8'))

    def recv(self):
        data = "".encode('utf-8')
        while True:
            try:
                data = data + self.sock.recv(1024)
                return loads(data)
            except ValueError:
                continue

    def callback(self, data):
        self.send(data)
        return self.recv()
