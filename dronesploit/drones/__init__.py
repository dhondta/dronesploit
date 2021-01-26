# -*- coding: UTF-8 -*-
import ast
import socket
from sploitkit import Module
from time import sleep, time

from ..wifi import DeauthMixin


class DroneModule(Module, DeauthMixin):
    """ Generic Module proxy class for defining multiple common utility methods for drones. """
    def preload(self):
        if 'TARGET' not in self.config.keys():
            raise NotImplementedError("DroneModule must have a TARGET option")
        targets = self.config.option('TARGET').choices
        if len(targets) == 0:
            self.logger.warning("No {} target connected yet ; please use the 'scan' and 'connect' commands"
                                .format(self.drone))
            return False
        self.config['TARGET'] = targets[0]
    
    def prerun(self):
        for o in self.config.options():
            o.value
        ip = self.config.option("IP").value
        if self.console._jobs.call("ping -c 2 {} -w 3".format(ip)) != 0:
            self.logger.warning("Target seems to be down")
            return False
    
    def send_command(self, *args, **kwargs):
        self._last_cmd_resp = None
        fly_params = getattr(self, 'fly_params', {})
        sock_type = fly_params.get('socket', socket.SOCK_STREAM)
        s = socket.socket(socket.AF_INET, sock_type)
        timeout = kwargs.get('timeout', 10)
        s.settimeout(timeout)
        success = False
        try:
            payload = fly_params.get('format', "%s") % args
        except Exception as e:
            self.logger.error("Bad command payload format ({})".format(e))
            return False
        target_addr = (self.config.option("IP").value, self.config.option("FLYCTL_PORT").value)
        command_result = fly_params.get('result', lambda r: r)
        self._last_cmd_resp = None
        fly_params.get('pre', lambda *a: None)(s, target_addr, fly_params)
        if sock_type == socket.SOCK_STREAM:
            try:
                s.connect(target_addr)
                self.logger.debug("Send: " + payload)
                s.send(payload.encode())
                r = s.recv(1024).strip(b" \x00").decode()
                self.logger.debug("Recv: {}".format(r or "empty response"))
                if len(r) > 0:
                    self._last_cmd_resp = r = ast.literal_eval(r)
                    success = command_result(r)
                    if not success:
                        self.logger.failure("Command failed")
                    return success
                else:
                    self._last_cmd_resp = ""
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
        elif sock_type == socket.SOCK_DGRAM:
            success = None
            try:
                self.logger.debug("Send: " + payload)
                s.sendto(payload.encode(), target_addr)
                start = time()
                while time() - start < timeout:
                    resp, addr = s.recvfrom(1024)
                    if addr != target_addr:
                        continue
                    self._last_cmd_resp = resp
                    success = command_result(resp)
                    if success in [True, False]:
                        break
            except socket.timeout:
                self.logger.warning("Timed out")
            except Exception as e:
                self.logger.failure("Command failed ({})".format(e))
            finally:
                s.close()
                return success
        fly_params.get('post', lambda *a: None)(s, target_addr, fly_params)

