#!/usr/bin/env python3
import sys
from os import path, remove

from lib.stdout import color
from src.build.build import Build


def main() -> None:
    color.b_grn.print("[Building]")
    build = Build()
    if not path.isfile(build.conf_ini):
        build.make_config()
        color.grn.print("Initiated config.ini")
        color.ylw.print("Enter target's IP in config then run make again")
        sys.exit(0)
    ipv4 = build.parse_config()
    build.verify_ipv4(ipv4)
    build.write_ip_file(ipv4)
    color.grn.print("Building Package:")
    build.make_exe()
    color.ylw.print("Build complete\n")
    build.move_client()
    remove(build.conf_ini)
    build.write_ip_file('"Enter target IP here"')
