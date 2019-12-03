from tinyscript import *

from lib import DronesploitConsole


def at_exit():
    subprocess.call("service network-manager restart", shell=True)
    subprocess.call("reset", shell=True)


if __name__ == '__main__':
    parser.add_argument("--dev", action="store_true", help="development mode")
    initialize(exit_at_interrupt=False, sudo=True)
    DronesploitConsole(
        "DroneSploit",
        banner_section_styles={'title': {'fgcolor': "random"}},
        dev=args.dev,
    ).start()
