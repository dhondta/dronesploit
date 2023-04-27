# -*- coding: UTF-8 -*-
import re


__all__ = ["drone_filter", "re"]


__r = lambda x: re.compile(x + r"[_\-][0-9A-Z]{4,20}")


DRONE_REGEX = {
    'DJI Mavic':        [__r(r"MAVIC_AIR"),
                         __r(r"Mavic")],
    'DJI Phantom':      __r(r"PHANTOM\d?"),
    'DJI Spark':        __r(r"Spark"),
    'DJI Tello':        __r(r"TELLO"),
    'FPV Racing Drone': __r(r"WIFI_FPV"),
    'Hobbico C-me':     __r(r"C-me"),
    'Hobbico Flitt':    __r(r"Flitt"),
    'Hubsan':           __r(r"HUBSAN_[A-Z]{1,2}\d+[A-Z]?"),
    'Parrot Bebop':     __r(r"Bebop\d?"),
    'Unknown':          __r(r"Drone\d?"),
}


def drone_filter(essid, model=None):
    r = {k: (v if isinstance(v, list) else [v]) for k, v in DRONE_REGEX.items()}
    if model is not None:
        if model not in r.keys():
            raise ValueError("Bad drone model")
        r = {model: r[model]}
    for _, rl in r.items():
        for regex in rl:
            if regex.match(str(essid), re.I):
                return True
    return False

