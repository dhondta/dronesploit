# -*- coding: UTF-8 -*-
from lib.wifi import *


class SniffModule(WifiModule, ScanMixin):
    """ Module proxy class for defining the .run() method handling SSID
         detection.
    
    Author:  Alexandre D'Hondt
    Version: 1.0
    """
    config = Config({
        Option(
            'TIMEOUT',
            "WiFi beacon capture timeout",
            False,
            validate=lambda s, x: str(x).isdigit() and int(x) > 0,
        ): 300,
    })
    path = "auxiliary/wifi"
    requirements = {'state': {"INTERFACES": {None: True}}}
    
    def run(self):
        _ = [i for i, mon in self.console.state['INTERFACES'].items() if mon]
        ScanMixin.run(self, _[0], self.config.option('TIMEOUT').value)


class FindSsids(SniffModule):
    """ Scan for any SSID's. """
    def run(self):
        super(FindSsids, self).run()


class FindTargets(SniffModule):
    """ Scan for SSID's of known drones. """
    def run(self):
        def drone_filter(essid, *data):
            for _, regex in DRONE_REGEX.items():
                if regex.match(essid):
                    return True
            return False
        super(FindTargets, self).run(filter_func=drone_filter)
