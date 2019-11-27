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
    """ Module proxy class for defining multiple common utility methods for
         DJI drones.
    
    Author:  Alexandre D'Hondt
    Email:   alexandre@hotmail.com
    Version: 1.0
    """
    def send_command(self, *args, **kwargs):
        raise NotImplementedError


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
            choices=lambda o: [e for e in o.state['TARGETS'].keys() \
                               if drone_filter(e, "DJI Tello")],
        ): None,
    })
    path = "command/dji/tello"
