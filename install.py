#!/usr/bin/env python3
import importlib.util
import sys
from argparse import ArgumentParser
from configparser import ConfigParser
from glob import glob
from os import getcwd, name
from os import path, remove
from shutil import copyfile
from shutil import rmtree
from subprocess import call

from resheller.src.stdout.color import Color


class Make:
    """Call to resolve config paths and create uninitiated configs"""

    def __init__(self):
        self.repo = getcwd()
        self.conf_ini = path.join(self.repo, 'config.ini')
        self.package = path.join(self.repo, "resheller")
        self.client_dir = path.join(self.package, "src", "client")
        self.ip_file = path.join(self.client_dir, "ip.py")
        self.tab = 4 * " "
        self.items = []

    def write_ip_file(self, ip='"insert ip here"'):
        with open(self.ip_file, "w") as file:
            file.write(f"#!/usr/bin/env python3\n\n\n"
                       f"def get_ip():"
                       f"\n    return {ip}\n")
            file.close()

    def install_requirements(self):
        requirements = path.join(self.repo, "requirements.txt")
        with open(requirements, "r") as reqs:
            lines = reqs.readlines()
            reqs.close()
        for line in lines:
            line = line[:-1]
            line = line.split("=")
            line = line[0]
            if not importlib.util.find_spec(line):
                call([sys.executable, "-m", "pip", "install", line])
        prompt = f"{self.tab}Package requirements satisfied\n"
        print(Color(prompt).ylw())

    def make_config(self):
        def_ini = path.join(self.package, "lib", 'default.ini')
        if not path.isfile(self.conf_ini):
            if not path.isfile(self.conf_ini):
                copyfile(def_ini, self.conf_ini)
            print(Color(f"Initiated config.ini in {self.repo}").grn())
            prompt = f"{self.tab}Configure config.ini then run this again"
            print(Color(prompt).ylw())
            exit(0)

    def get_ip(self):
        config = ConfigParser()
        conf_ini = path.join(getcwd(), 'config.ini')
        config.read(conf_ini)
        ip = config["IP"]["server"]
        if "insert ip here" in ip:
            prompt = "Enter host IP in config file then run python3 install.py"
            print(Color(prompt).red())
            exit(0)
        self.write_ip_file(ip)

    def get_exe(self):
        client = "client"
        if name == "nt":
            client = "client.exe"
        return path.join(self.repo, "dist", client)

    def make_exe(self):
        client_py = path.join(self.client_dir, "client.py")
        client_exe = self.get_exe()
        if path.isfile(client_exe):
            print(Color(f"{self.tab}Resheller already installed").ylw())
            print("\nHint: Run install.py -r to reinstall")
        else:
            call(["pyinstaller", "--onefile", "--noconsole", client_py])

    def install(self):
        print(Color("[Installing]").b_grn())
        print(Color("Installing package requirements:").grn())
        self.install_requirements()
        self.make_config()
        self.get_ip()
        print(Color("Installing package").grn())
        self.make_exe()

    def rm_dirs(self):
        for i in ["build", "dist"]:
            if path.isdir(i):
                rmtree(i)
                print(self.tab + Color(path.basename(i)).ylw())
                self.items.append(path.basename(i))

    def rm_ini(self):
        if path.isfile(self.conf_ini):
            remove(self.conf_ini)
            print(self.tab + Color(path.basename(self.conf_ini)).ylw())
            self.items.append(path.basename(self.conf_ini))

    def rm_specs(self):
        specs = glob("*.spec")
        for spec in specs:
            try:
                remove(spec)
                print(self.tab + Color(path.basename(spec)).ylw())
                self.items.append(path.basename(spec))
            except FileNotFoundError:
                pass

    def get_result(self):
        confirm = ''.join([str(f'{item}, ') for item in self.items])
        confirm = confirm.replace(", and,", " and")
        return confirm[:-2]

    def punctuate(self):
        length = len(self.items)
        if length > 1:
            self.items.insert((length - 1), "and")
        print()

    def clean(self):
        print(Color("[Cleaning]").b_grn())
        print(Color("Removing:").grn())
        self.rm_dirs()
        self.rm_ini()
        self.rm_specs()
        self.punctuate()
        if self.items:
            prompt = self.get_result()
            print(Color("Removed:").grn())
            print(Color(self.tab + prompt).ylw())
        else:
            print(Color("Nothing to Remove").ylw())
        self.write_ip_file()

    def reinstall(self):
        client_exe = self.get_exe()
        print(Color("[Reinstalling]").b_grn())
        if path.isfile(client_exe):
            self.clean()
            print()
            self.install()
        else:
            print(Color("Resheller is not installed").ylw())


def argument_parser():
    parser = ArgumentParser()
    parser.add_argument("-c", "--clean", action="store_true")
    parser.add_argument("-r", "--reinstall", action="store_true")
    return parser.parse_args()


def installer():
    make = Make()
    args = argument_parser()
    if args.clean:
        make.clean()
    elif args.reinstall:
        make.reinstall()
    else:
        make.install()


if __name__ == '__main__':
    installer()
