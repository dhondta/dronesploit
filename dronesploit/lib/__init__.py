#!/usr/bin/python3
import re
from sploitkit import FrameworkConsole
from sploitkit.utils.dict import ExpiringDict


class DronesploitConsole(FrameworkConsole):
    sources = {
        'banners':   "./dronesploit/banners",
        'entities':  ["./dronesploit/commands", "./dronesploit/models", "./dronesploit/modules"],
        'libraries': "./dronesploit",
    }
    exclude = ["root/test", "root/help"]
    
    def __init__(self, *args, **kwargs):
        self.interfaces
        self.state['TARGETS'] = ExpiringDict(max_age=300)
        self.state['STATIONS'] = ExpiringDict(max_age=300)
        self.state['PASSWORDS'] = {}
        super(DronesploitConsole, self).__init__(*args, **kwargs)
        for c, n, e in self.issues(category="system"):
            print(c, n, e)
    
    @property
    def connected_targets(self):
        return [x[1] for x in self.state['INTERFACES'].values() if x[1] is not None]
    
    @property
    def interfaces(self):
        d = self.state['INTERFACES'] = {}
        out = self._jobs.run("iwconfig", no_debug=True)[0]
        for i in re.split(r"\n\s*\n", out):
            if i == "":
                continue
            iface = i.split()[0]
            if "no wireless extensions" not in i:
                mon = "Mode:Monitor" in i
                mac = None
                ifcfg = self._jobs.run("ifconfig", no_debug=True)[0]
                try:
                    ssid = i.split("ESSID:\"", 1)[1].split("\"", 1)[0]
                    for j in re.split(r"\n\s*\n", ifcfg):
                        if j.startswith(iface + ":"):
                            mac = j.split("ether ")[1].split()[0].upper()
                except IndexError:
                    ssid = None
                    for j in re.split(r"\n\s*\n", ifcfg):
                        if j.startswith(iface + ":") and "unspec " in j:
                            mac = ":".join(j.split("unspec ")[1].split("-")[:6])
                d[iface] = [mon, ssid, mac]
        return d.keys()
    
    @property
    def man_interfaces(self):
        return [i for i, x in self.state['INTERFACES'].items() if not x[0]]
    
    @property
    def mon_interfaces(self):
        return [i for i, x in self.state['INTERFACES'].items() if x[0]]
    
    @property
    def self_mac_addresses(self):
        return [x[2] for x in self.state['INTERFACES'].values() if x[2] is not None]

