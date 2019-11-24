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
    
    def run(self, filter_func=lambda *a, **kw: True):
        self._filter_func = filter_func
        ScanMixin.run(self, self.config.option('INTERFACE').value,
                            self.config.option('TIMEOUT').value)
        delattr(self, "_filter_func")


class FindSsids(SniffModule):
    """ Scan for any SSID's. """
    def run(self):
        super(FindSsids, self).run()


class FindTargets(SniffModule):
    """ Scan for SSID's of known drones. """
    def run(self):
        super(FindTargets, self).run(filter_func=drone_filter)
