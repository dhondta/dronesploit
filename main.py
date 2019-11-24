#!/usr/bin/python3
from sploitkit import FrameworkConsole
from sploitkit.utils.dict import ExpiringDict
from tinyscript import *


class DronesploitConsole(FrameworkConsole):
    sources = {
        'banners':   "./banners",
        'libraries': "./lib",
    }
    exclude = ["root/test", "root/help"]
    
    def __init__(self, *args, **kwargs):
        self.interfaces
        self.state['TARGETS'] = ExpiringDict(max_age=300)
        super(DronesploitConsole, self).__init__(*args, **kwargs)
    
    @property
    def interfaces(self):
        d = self.state['INTERFACES'] = {}
        out = self._jobs.run("iwconfig", no_debug=True)[0]
        ifaces = re.split(r"\n\s*\n", out)
        for i in ifaces:
            if "no wireless extensions" not in i:
                d[i.split()[0]] = "Mode:Monitor" in i
        return d.keys()
    
    @property
    def mon_interfaces(self):
        return [i for i, mon in self.state['INTERFACES'].items() if mon]


if __name__ == '__main__':
    parser.add_argument("--dev", action="store_true", help="development mode")
    initialize(exit_at_interrupt=False, sudo=True)
    DronesploitConsole(
        "DroneSploit",
        banner_section_styles={'title': {'fgcolor': "random"}},
        dev=args.dev,
    ).start()
