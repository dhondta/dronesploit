# -*- coding: UTF-8 -*-
import re
from sploitkit import Config, Module, Option


class WifiModule(Module):
    config = Config({
        Option(
            'INTERFACE',
            "WiFi interface",
            True,
        ): "wlx9cefd5fd9a0c",
    })
    path = "auxiliary/wifi"


class Wifi2Module(WifiModule):
    config = Config({
        Option(
            'OTHER',
            "Test",
            True,
        ): "test",
    })
    path = "auxiliary/wifi"


class Deauth(Wifi2Module):
    """ Deauthenticate the target given its BSSID.
    
    Author:  Yannick Pasquazzo
    Version: 1.0
    """
    config = Config({
        Option(
            'DEAUTH',
            "Test",
            True,
        ): "test",
    })
    requirements = {'system': ["aireplay-ng"]}
    
    def run(self):
        print(self.config)
        self.logger.info(self.console.state.get('MONITOR_IF'))
        self.logger.info(self.console.state.get('TARGETS'))


class MonitorMode(WifiModule):
    """ Set the given WiFi interface in monitor mode.
    
    Author:  Yannick Pasquazzo
    Version: 1.0
    """
    config = Config({
        Option(
            'MONITOR',
            "Test",
            True,
        ): "test",
    })
    requirements = {'system': ["airmon-ng"]}
    
    def run(self):
        # FIXME: what if IF already in monitor mode ??
        self.console.state.setdefault('MONITOR_IF', None)
        if self.console.state['MONITOR_IF'] is None:
            interface = self.config.option("INTERFACE").value
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
            interface = self.console.state['MONITOR_IF']
            # turn off monitor mode
            self.console._jobs.run("sudo airmon-ng stop {}".format(interface))
            self.console.state['MONITOR_IF'] = None
            self.console.state['MONITOR_IF_ID'] = None
            self.logger.info("{}'s monitor mode was disabled".format(interface))


class Wpa2pskCrack(WifiModule):
    requirements = {'system': ["aircrack-ng"]}
    #TODO
