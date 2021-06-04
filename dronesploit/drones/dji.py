# -*- coding: UTF-8 -*-
import ast
import socket
import time
from datetime import datetime
from sploitkit import *

from . import DroneModule
from ..wifi import drone_filter


__all__ = ["DJIModule"]


class DJIModule(DroneModule):
    """ Module proxy class for defining multiple common utility methods for DJI drones.
    
    Author:  Alexandre D'Hondt
    Email:   alexandre.dhondt@gmail.com
    Version: 1.0
    """
    pass


class TelloModule(DJIModule):
    """ Module proxy class holding the default parameter of a Tello. """
    config = Config({
        Option(
            'IP',
            "IP address of drone's AP",
            True,
        ): "192.168.10.1",
        Option(
            'FLYCTL_PORT',
            "Fly controller port",
            True,
        ): 8889,
        Option(
            'TARGET',
            "Target's SSID",
            True,
            choices=lambda o: [e for e in o.state['TARGETS'].keys() if drone_filter(e, o.module.drone) and \
                               e in o.console.root.connected_targets],
        ): None,
    })
    drone = "DJI Tello"
    fly_params = {
        'commands': {
            'emergency': ("Emergency stop...", "Emergency stop not done"),
            'land':      ("Landing the target...", "Landing not done"),
            'takeoff':   ("Taking off the target...", "Takeoff not done"),
            'temp?': ("Getting temperature...", "Temperature not retrieved"),
        },
        'post':   lambda s, t, p: s.sendto(b"command", t),
        'pre':    lambda s, t, p: s.sendto(b"command", t),
        'result': lambda r: True if r.strip().lower() == b"ok" else False if r.strip().lower() == b"unknown command!" \
                            else None,
        'socket': socket.SOCK_DGRAM,
    }
    path = "command/dji/tello"
    
    def _change_ap_creds(self, ssid, pswd, new_ssid=True):
        i = ["password", "SSID"][new_ssid]
        self.logger.info("Changing %s..." % i)
        r = self.send_command("wifi '%s' '%s'" % (ssid, pswd))
        self._feedback(r, "AP %s not changed" % i)
        if not new_ssid:
            self.console.state['TARGETS'][ssid]['password'] = pswd
        self.console.state['PASSWORDS'][ssid] = pswd
        return r
    
    def _send_udp_command(self, command):
        msg = TelloModule.fly_params['commands'].get(command)
        if msg is not None:
            self.logger.info(msg[0])
            r = self.send_command(command)
            self._feedback(r, msg[1])
            return r
        raise Exception("Bad UDP command")

