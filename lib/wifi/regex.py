# -*- coding: UTF-8 -*-
import re


__all__ = ["DRONE_REGEX", "IW_REGEX", "STATION_REGEX", "TARGET_REGEX",
           "WPA_HANDSHAKE_REGEX"]


__regex_set = lambda x: re.compile(x + r"[_\-][0-9a-zA-Z]{4,20}")


DRONE_REGEX = {
    'Hobbico C-me':   __regex_set(r"C-me"),
    'Hobbico Flitt':  __regex_set(r"Flitt"),
    'Parrot Bebop':   __regex_set(r"Bebop"),
    'Parrot Bebop 2': __regex_set(r"Bebop2"),
    'DJI Tello':      __regex_set(r"TELLO"),
}

IW_REGEX = re.compile(r"(?m)(?P<name>[a-z][a-z0-9]*)\s+"
                      r"IEEE\s(?P<techno>[a-zA-Z0-9\.])\s+"
                      r"Mode\:\s*(?P<mode>[A-Z][a-z]+)\s+")

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
