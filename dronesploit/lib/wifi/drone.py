# -*- coding: UTF-8 -*-
import re


__all__ = ["drone_filter", "re"]


__regex_set = lambda x: re.compile(x + r"[_\-][0-9a-zA-Z]{4,20}")


DRONE_REGEX = {
    'DJI Tello':        __regex_set(r"TELLO"),
    'FPV Racing Drone': __regex_set(r"WIFI_FPV"),
    'Hobbico C-me':     __regex_set(r"C-me"),
    'Hobbico Flitt':    __regex_set(r"Flitt"),
    'Parrot Bebop':     __regex_set(r"Bebop"),
    'Parrot Bebop 2':   __regex_set(r"Bebop2"),
}


def drone_filter(essid, model=None):
    regexes = DRONE_REGEX
    if model is not None:
        if model not in DRONE_REGEX.keys():
            raise ValueError("Bad drone model")
        regexes = {model: DRONE_REGEX[model]}
    for _, regex in regexes.items():
        if regex.match(str(essid)):
            return True
    return False
