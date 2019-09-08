# -*- coding: UTF-8 -*-
from sploitkit.utils.dict import ExpiringDict

from generic import *


DRONE_REGEX = {
#    'Bebop':  re.compile(r""),
    'C-me':   re.compile(r"C-me[_\-][0-9a-f]{5}"),
    'Flitt':  re.compile(r"Flitt[_\-]\d{6}"),
#    'Parrot': re.compile(r""),
#    'Tello':  re.compile(r""),
}


class SniffModule(Module):
    config = Config({
        Option(
            'DURATION',
            "WiFi beacon capture duration",
            False,
            validate=lambda s, x: isinstance(x, int),
        ): 300,
    })
    path = "auxiliary/wifi"

    def run(self, filter_func=lambda *x: True):
        self.logger.warning("Press Ctrl+C to interrupt")
        mon_if = self.console.state['MONITOR_IF']
        if mon_if is None:
            self.logger.warning("No interface set in monitor mode")
            return
        to = self.config.option("DURATION").value
        self.console.state.setdefault("TARGETS", ExpiringDict(max_age=300))
        self.console.state['TARGETS'].unlock()
        for line in self.console._jobs.run_iter("sudo airodump-ng {}"
                                                .format(mon_if), timeout=to):
            _ = TARGET_REGEX.search(line)
            if _ is None:
                continue
            data = [
                _.group("essid"),
                _.group("bssid"),
                int(_.group("channel")),
                _.group("enc"),
                _.group("cipher"),
                _.group("auth"),
            ]
            if filter_func(*data):
                if data[0] not in self.console.state['TARGETS'].keys():
                    self.console.state['TARGETS'][data[0]] = data[1:]
                    self.logger.info("{} ({})".format(*data[:2]))
        self.console.state['TARGETS'].lock()


class FindSsids(SniffModule):
    """ Scan for any SSID's.
    
    Author:  Alexandre D'Hondt
    Version: 1.0
    """
    def run(self):
        super(FindSsids, self).run()


class FindTargets(SniffModule):
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
        super(FindTargets, self).run(filter_func=drone_filter)
