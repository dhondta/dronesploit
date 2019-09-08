# -*- coding: UTF-8 -*-
import re
from time import time
from sploitkit import Config, Module, Option, Path


__all__ = ["re", "time", "Config", "Module", "Option", "Path", "WifiModule",
           "WifiAttackModule", "STATION_REGEX", "TARGET_REGEX",
           "WPA_HANDSHAKE_REGEX"]


STATION_REGEX = re.compile(r"^\s*(?P<bssid>(?:[0-9A-F]{2}\:){5}[0-9A-F]{2})\s+"
                           r"(?P<station>(?:[0-9A-F]{2}\:){5}[0-9A-F]{2})\s+")
TARGET_REGEX = re.compile(r"^\s*(?P<bssid>(?:[0-9A-F]{2}\:){5}[0-9A-F]{2})\s+"
                          r"(?P<power>\-?\d+)\s+"
                          r"(?P<beacons>\d+)\s+"
                          r"(?P<data>\d+)\s+"
                          r"(?P<prate>\d+)\s+"
                          r"(?P<channel>\d+)\s+"
                          r"(?P<mb>\w+)\s+"
                          r"(?P<enc>\w+)\s+"
                          r"(?P<cipher>\w+)\s+"
                          r"(?P<auth>\w+)\s+"
                          r"(?P<essid>[\w\-\.]+)\s*$")
WPA_HANDSHAKE_REGEX = re.compile(r"WPA handshake\:\s+"
                                 r"(?P<bssid>(?:[0-9A-F]{2}\:){5}[0-9A-F]{2})")


class WifiModule(Module):
    config = Config({
        Option(
            'INTERFACE',
            "WiFi interface",
            True,
        ): "wlx9cefd5fd9a0d",
    })
    path = "auxiliary/wifi"


class WifiAttackModule(WifiModule):
    config = Config({
        Option(
            'BSSID',
            "AP's BSSID",
            True,
        ): "00:00:00:00:00:00",
    })
    
    def preamble(self):
        if self.console.state.get('MONITOR_IF') is None:
            self.logger.warning("No interface in monitor mode defined ; please"
                                " use module 'auxiliary/wifi/monitor_mode'")
            return False
        if self.console.state.get('TARGETS') is None or \
            len(self.console.state['TARGETS']) == 0:
            self.logger.warning("No target available yet ; please use module "
                                "'auxiliary/wifi/find_*'")
            return False
        _ = self.console.state['TARGETS']
        self.config['BSSID'] = v = _[list(_.keys())[0]][0]
        self.logger.debug("BSSID => {}".format(v))
        self.config.option('BSSID').choices = [v[0] for k, v in _.items()]
        return True


class MonitorMode(WifiModule):
    """ Set the given WiFi interface in monitor mode.
    
    Author:  Yannick Pasquazzo
    Version: 1.0
    """
    requirements = {'system': ["airmon-ng"]}
    
    def run(self):
        # FIXME: what if IF already in monitor mode ??
        self.console.state.setdefault('MONITOR_IF', None)
        interface = self.config.option("INTERFACE").value
        if self.console.state['MONITOR_IF'] is None:
            # turn off the targeted interface
            self.console._jobs.run("sudo airmon-ng stop {}".format(interface))
            # kill processes using this interface
            self.console._jobs.run("sudo airmon-ng check kill")
            # turn on monitor mode ; this will rename the interface
            out, err = self.console._jobs.run("sudo airmon-ng start {}"
                                              .format(interface), stdin="y\n")
            new, name = None, None
            for line in out.split("\n"):
                if "monitor mode" in line:
                    _ = re.search(r"\[([a-z]+\d+)\](\w+)", line)
                    if _ is not None:
                        name, new = _.group(1), _.group(2)
                    break
            if new is None:
                self.logger.error("Could not set {} to monitor mode"
                                  .format(interface))
                return
            # rename the interface in the console config
            self.console.state['MONITOR_IF'] = new
            self.console.state['MONITOR_IF_ID'] = name
            self.logger.info("{} has been set to monitor mode on {}"
                             .format(interface, new))
            # ensure the interface is not soft-blocked
            out, _ = self.console._jobs.run("sudo rfkill list")
            for line in out.splitlines():
                parts = line.split(":", 2)
                if parts[1].strip() == name:
                    self.console._jobs.run("sudo rfkill unblock %s" % parts[0])
        else:
            mon_if = self.console.state['MONITOR_IF']
            # turn off monitor mode
            self.console._jobs.run("sudo airmon-ng stop {}".format(mon_if))
            self.console.state['MONITOR_IF'] = None
            self.console.state['MONITOR_IF_ID'] = None
            self.logger.info("{} has been set back to managed mode"
                             .format(interface))
