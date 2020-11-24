#!/usr/bin/python3
# -*- coding: utf-8 -*-
from dronesploit.__info__ import __author__, __copyright__, __email__, __license__, __version__
from dronesploit.lib import DronesploitConsole as BaseConsole
from tinyscript import *


__script__ = "dronesploit"
__doc__    = """
Dronesploit framework's launcher script.
"""


def at_exit():
    pass#subprocess.call("service network-manager restart", shell=True)
    #subprocess.call("reset", shell=True)


class DronesploitConsole(BaseConsole):
    sources = {
        'banners':   "banners",
        'entities':  ["commands", "models", "modules"],
        'libraries': ".",
    }


def main():
    parser.add_argument("--dev", action="store_true", help="development mode")
    initialize(exit_at_interrupt=False, sudo=True)
    c = DronesploitConsole(
        __scriptname__,
        banner_section_styles={'title': {'fgcolor': "random"}},
        dev=args.dev,
    )
    if args.verbose:
        c.execute("set DEBUG true")
    c.start()

