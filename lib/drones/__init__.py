# -*- coding: UTF-8 -*-
import ast
import socket
from sploitkit import Module


class DroneModule(Module):
    """ Generic Module proxy class for defining multiple common utility methods
         for drones. """
    def preload(self):
        if self.console.state.get('TARGETS') is None or \
            len(self.console.state['TARGETS']) == 0:
            self.logger.warning("No target available yet ; please use the "
                                "'scan' command")
            return False
        ip = self.config.option("IP").value
        if self.console._jobs.call("ping -c 1 -W 2 {}".format(ip)) != 0:
            self.logger.warning("Target seems to be down")
            return False
        return True

    def send_command(self, *args, **kwargs):
        self._last_cmd_resp = None
        sock_type = getattr(self, 'sock_type', socket.SOCK_STREAM)
        s = socket.socket(socket.AF_INET, sock_type)
        s.connect((self.config.option("IP").value,
                   self.config.option("FLYCTL_PORT").value))
        payload = getattr(self, 'payload_format', "") % args
        self.logger.debug("Send: " + payload)
        success = False
        try:
            s.send(payload.encode())
            r = ast.literal_eval(s.recv(1024).strip(b" \x00").decode())
            success = r['RESULT'] == 0
            self.logger.debug("Recv: {}".format(r))
            if not success:
                self.logger.failure("Command failed")
            self._last_cmd_resp = r
        except Exception as e:
            self.logger.failure("Command failed ({})".format(e))
        s.close()
        return success
