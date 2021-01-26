# -*- coding: UTF-8 -*-
from time import time
from sploitkit import Config, Module, Option
from tinyscript.helpers import Path

from .drone import *
from .mixin import *


__all__ = [
    "re",
    "drone_filter", "time",
    "Config", "Module", "Option", "Path",
    "DeauthMixin", "ScanMixin", "WifiConnectMixin",
    "WifiModule", "WifiAttackModule",
    "STATION_REGEX",
]


class WifiModule(Module):
    """ Module proxy class for WiFi-related modules """
    config = Config({
        Option(
            'INTERFACE',
            "WiFi interface in monitor mode",
            True,
            choices=lambda o: o.root.mon_interfaces,
        ): None,
    })
    path = "auxiliary/wifi"
    requirements = {'state': {'INTERFACES': {None: [True, None, None]}}, 'system': ["wireless-tools/iwconfig"]}
    requirements_messages = {'state': {'INTERFACES': "At least one interface in monitor mode is required"}}
    
    def preload(self):
        return self.prerun()
    
    def prerun(self):
        if len(self.console.root.mon_interfaces) == 0:
            self.logger.warning("No interface in monitor mode defined ; please use the 'toggle' command")
            return False
        self.config['INTERFACE'] = self.console.root.mon_interfaces[0]


class WifiAttackModule(WifiModule):
    """ Module proxy class for WiFi-related modules handling a target """
    config = Config({
        Option(
            'ESSID',
            "Target AP's ESSID",
            True,
            choices=lambda o: o.state['TARGETS'].keys()
        ): None,
    })
    
    def preload(self):
        if super(WifiAttackModule, self).preload() is False:
            return False
        t = self.console.state['TARGETS']
        if len(t) == 0:
            self.logger.warning("No target available yet ; please use the 'scan' command")
            return False
        self.config['ESSID'] = v = t[list(t.keys())[0]]['essid']
        self.logger.debug("ESSID => {}".format(v))

