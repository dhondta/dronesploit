#!/usr/bin/python3
import os
from sploitkit import FrameworkConsole


class DronesploitConsole(FrameworkConsole):
    sources = {
        'banners': "./banners",
    }
    exclude = ["root/test", "root/help"]


if __name__ == '__main__':
    if os.geteuid() != 0:
        print("This should be run as sudo")
    else:
        DronesploitConsole(
            "DroneSploit",
            banner_section_styles={'title': {'fgcolor': "random"}},
        ).start()
