# -*- coding: UTF-8 -*-
from time import time
from sploitkit import Config, Module, Option, Path

from .regex import *
from .wpa import *


__all__ = [
    "drone_filter", "time",
    "Config", "Module", "Option", "Path",
    "ScanMixin", "WifiModule", "WifiAttackModule", "WPAConnectMixin",
    "DRONE_REGEX", "STATION_REGEX", "TARGET_REGEX", "WPA_HANDSHAKE_REGEX",
]


def drone_filter(essid, model=None):
    regexes = DRONE_REGEX
    if model is not None:
        if model not in DRONE_REGEX.keys():
            raise ValueError("Bad drone model")
        regexes = {model: DRONE_REGEX[model]}
    for _, regex in DRONE_REGEX.items():
        if regex.match(essid):
            return True
    return False


class ScanMixin(object):
    """ Mixin class for use with Command and Module """
    def run(self, interface, timeout=300):
        self.logger.warning("Press Ctrl+C to interrupt")
        t = self.console.state['TARGETS']
        t.unlock()
        cmd = "sudo airodump-ng {}".format(interface)
        try:
            for line in self.console._jobs.run_iter(cmd, timeout=int(timeout)):
                _ = TARGET_REGEX.search(line)
                if _ is None:
                    continue
                data = {}
                for k in ["essid", "bssid", "channel", "power", "enc", "cipher",
                          "auth"]:
                    v = _.group(k)
                    data[k] = int(v) if v.isdigit() else v
                data['password'] = None
                e = data['essid']
                if self._filter_func(e):
                    if e not in t.keys():
                        self.logger.info("Found {}".format(e))
                    else:
                        data['password'] = t[e].get('password')
                    t[e] = data
        finally:
            t.lock()


class WifiModule(Module):
    """ Module proxy class for WiFi-related modules """
    config = Config({
        Option(
            'INTERFACE',
            "WiFi interface in monitor mode",
            True,
            choices=lambda o: o.config.console.root.mon_interfaces,
        ): None,
    })
    path = "auxiliary/wifi"
    requirements = {'system': ["wireless-tools/iwconfig"]}
    
    def preload(self):
        return self.prerun()
    
    def prerun(self):
        if len(self.console.root.mon_interfaces) == 0:
            self.logger.warning("No interface in monitor mode defined ; please"
                                " use the 'toggle' command")
            return False
        self.config['INTERFACE'] = self.console.root.mon_interfaces[0]


class WifiAttackModule(WifiModule):
    """ Module proxy class for WiFi-related modules handling a target """
    config = Config({
        Option(
            'ESSID',
            "Target AP's ESSID",
            True,
            choices=lambda o: o.config.console.state['TARGETS'].keys()
        ): None,
    })
    
    def preload(self):
        if super(WifiAttackModule, self).preload() is False:
            return False
        _ = self.console.state['TARGETS']
        if len(_) == 0:
            self.logger.warning("No target available yet ; please use the "
                                "'scan' command")
            return False
        self.config['ESSID'] = v = _[list(_.keys())[0]]['essid']
        self.logger.debug("ESSID => {}".format(v))
