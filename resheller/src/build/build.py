#!/usr/bin/env python3
import sys
from configparser import ConfigParser
from ipaddress import IPv4Address
from os import path, name, rename
from shutil import copyfile
from subprocess import call, DEVNULL

from root_finder import get_project_root

from lib.stdout import color


class Build:
    """Call to resolve config paths and create uninitiated configs"""

    def __init__(self) -> None:
        self.repo = get_project_root("resheller")
        self.conf_ini = path.join(self.repo, "config.ini")
        self.package = path.join(self.repo, "resheller")

    def write_ip_file(self, ipv4: str) -> None:
        """Write importable module with data taken from the `config.ini` file

        :param ipv4: IP of target host or instruction to add IP
        """
        ip_file = path.join(self.package, "src", "client", "ip.py")
        with open(ip_file, "w") as file:
            file.write("#!/usr/bin/env python3\n")
            file.write('"""resheller.src.client.ip"""\n\n\n')
            file.write("def get_ip():\n")
            file.write(f"    return {ipv4}\n")

    def make_config(self) -> None:
        """Copy a new `config.ini` file from default template, `default.ini`"""
        def_ini = path.join(self.package, "lib", "default.ini")
        copyfile(def_ini, self.conf_ini)

    def parse_config(self) -> str:
        """Read IP address from the `config.ini` file

        :return: Configured IP address
        """
        config = ConfigParser()
        config.read(self.conf_ini)
        return config["IP"]["server"]

    @staticmethod
    def verify_ipv4(ipv4: str) -> None:
        """Ensure IP address is a valid IPv4 address

        :param ipv4: Configured IP address
        """
        try:
            IPv4Address(ipv4.strip('"'))
        except ValueError as err:
            if "Enter target IP here" in ipv4:
                color.red.print("Enter target's IP in the `config.ini` file")
            else:
                color.b_red.print(f"Not a valid IPv4 Address\n   {err}")
            sys.exit(0)

    def make_exe(self) -> None:
        client_py = path.join(self.package, "client.py")
        cmd = f"pyinstaller --onefile --noconsole {client_py}"
        call(cmd, stdout=DEVNULL, stderr=DEVNULL, shell=True)

    def move_client(self) -> None:
        client_exe = "client.exe" if name == "nt" else "client"
        client_src = path.join(self.repo, "dist", client_exe)
        client_dst = path.join(self.repo, client_exe)
        rename(client_src, client_dst)
