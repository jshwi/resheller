#!/usr/bin/env python3
"""resheller.src.build.main"""
import sys
from os import path, remove

from lib.stdout import COLOR
from src.build.build import Build
from src.build.parser import parser


def main() -> None:
    """Run the build process initiated by build.py or Makefile"""
    args = parser()
    COLOR.b_grn.print("[Building]")
    build = Build(args)
    if not path.isfile(build.config):
        build.make_config()
        COLOR.grn.print("Initiated config.ini")
        COLOR.ylw.print("Enter target's IP in config then run make again")
        sys.exit(0)
    ipv4 = build.parse_config()
    if not build.verify_ipv4(ipv4):
        sys.exit(1)
    build.write_ip_py(ipv4)
    COLOR.grn.print("Building Package")
    if build.make_exe():
        COLOR.b_red.print("Error building client")
        sys.exit(1)
    else:
        COLOR.b_grn.print("Build successful\n")
    build.move_client()
    remove(build.config)
    build.write_ip_py('"Enter target IP here"')
