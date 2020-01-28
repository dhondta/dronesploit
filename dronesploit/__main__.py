#!/usr/bin/python3
import dronesploit
from dronesploit.lib import DronesploitConsole as BaseConsole
from tinyscript import *

from dronesploit.__info__ import __author__, __version__
__script__ = "dronesploit"
__copyright__ = "A. D'Hondt"
__license__ = "agpl-3.0"
__doc__ = """
Dronesploit framework's launcher script.
"""


DAT = os.path.join(sys.prefix, "local", "dronesploit")
PKG = os.path.dirname(dronesploit.__file__)


def at_exit():
    subprocess.call("service network-manager restart", shell=True)
    subprocess.call("reset", shell=True)


class DronesploitConsole(BaseConsole):
    sources = {
        'banners':   os.path.join(DAT, "banners"),
        'entities':  [os.path.join(DAT, f) for f in \
                      ["commands", "models", "modules"]],
        'libraries': PKG,
    }


def main():
    parser.add_argument("--dev", action="store_true", help="development mode")
    initialize(exit_at_interrupt=False, sudo=True)
    DronesploitConsole(
        "DroneSploit",
        banner_section_styles={'title': {'fgcolor': "random"}},
        dev=args.dev,
    ).start()
