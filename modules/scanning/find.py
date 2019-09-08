# -*- coding: UTF-8 -*-
import netaddr
import shlex
from scapy.all import *
from sploitkit import Config, Module, Option


DRONE_REGEX = {
#    'Bebop':  re.compile(r""),
    'C-me':   re.compile(r"C-me-[0-9a-f]{5}"),
    'Flitt':  re.compile(r"Flitt-\d{6}"),
#    'Parrot': re.compile(r""),
#    'Tello':  re.compile(r""),
}
EXTRA_OUI = {
    '90:AF:B7': "Hobbico Inc",
}
TARGET_REGEX = re.compile(r"^(?P<bssid>(?:[0-9A-F]{2}\:){5}[0-9A-F]{2})\s+"
                          r"(?P<power>\-?\d+)\s+"
                          r"(?P<beacons>\d+)\s+"
                          r"(?P<data>\d+)\s+"
                          r"(?P<prate>\d+)\s+"
                          r"(?P<channel>\d+)\s+"
                          r"(?P<mb>\w+)\s+"
                          r"(?P<enc>\w+)\s+"
                          r"(?P<cipher>\w+)\s+"
                          r"(?P<auth>\w+)\s+"
                          r"(?P<essid>[\w\-\.]+)$")


class FindModule(Module):
    config = Config({
        Option(
            'DURATION',
            "WiFi beacon capture duration",
            False,
            validate=lambda s, x: isinstance(x, int),
        ): 10,
    })

    def run(self, filter=lambda *x: True):
        mon_if = self.console.state['MONITOR_IF']
        if mon_if is None:
            self.logger.warning("No interface set in monitor mode")
            return
        to = self.config.option("DURATION").value
        self.console.state.setdefault("TARGETS", {})
        for line in self.console._jobs.run_iter("sudo airodump-ng {}"
                                                .format(mon_if), timeout=to):
            _ = TARGET_REGEX.search(line)
            if _ is None:
                continue
            data = [
                _.group("essid"),
                _.group("bssid"),
                _.group("channel"),
                _.group("enc"),
                _.group("cipher"),
                _.group("auth"),
            ]
            if filter(*data):
                self.console.state['TARGETS'][data[0]] = data[1:]
                self.logger.info("{} ({})".format(*data[:2]))


class FindSsids(FindModule):
    """ Scan for any SSID's.
    
    Author:  Alexandre D'Hondt
    Version: 1.0
    """
    def run(self):
        super(FindSsids, self).run()


class FindTargets(FindModule):
    """ Scan for SSID's of known drones.
    
    Author:  Alexandre D'Hondt
    Version: 1.0
    """
    def run(self):
        def drone_filter(essid, *data):
            for _, regex in DRONE_REGEX.items():
                if regex.match(essid):
                    return True
            return False
        super(FindSsids, self).run(filter=drone_filter)
